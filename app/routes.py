import calendar
from datetime import datetime, timedelta
from io import BytesIO

from flask import (
    Blueprint, flash, make_response, redirect, render_template,
    render_template_string, request, url_for
)
from flask_login import (
    current_user, login_required, login_user, logout_user
)
from sqlalchemy import extract, func
from werkzeug.security import check_password_hash, generate_password_hash
from xhtml2pdf import pisa

from app import db
from app.models import (
    Categoria, Compra, DetalleVenta, Producto, Usuario, Venta
)

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        clave = request.form['contraseña']
        usuario = Usuario.query.filter_by(correo=correo).first()

        if usuario and check_password_hash(usuario.contraseña, clave):
            if usuario.estado != 'activo':
                flash('Tu cuenta está inactiva. Contacta al administrador.')
                return redirect(url_for('main.login'))

            login_user(usuario)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Credenciales inválidas')
            return redirect(url_for('main.login'))

    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    from flask_login import current_user
    print("Usuario autenticado:", current_user.is_authenticated)
    print("Nombre:", current_user.nombre)
    return render_template('dashboard.html', usuario=current_user)

@main.route('/admin/registrar_usuario', methods=['GET', 'POST'])
@login_required
def registrar_usuario():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        cedula = request.form['cedula']
        correo = request.form['correo']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        clave = request.form['contraseña']
        rol = request.form['rol']

        if Usuario.query.filter_by(correo=correo).first():
            flash('El correo ya está registrado.')
        elif Usuario.query.filter_by(cedula=cedula).first():
            flash('La cédula ya está registrada.')
        else:
            nueva_clave = generate_password_hash(clave)
            nuevo_usuario = Usuario(
                nombre=nombre,
                cedula=cedula,
                correo=correo,
                telefono=telefono,
                direccion=direccion,
                contraseña=nueva_clave,
                rol=rol
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash('Usuario registrado correctamente.')
            return redirect(url_for('main.dashboard'))

    return render_template('registrar_usuario.html')

# Mostrar productos (admin)
@main.route('/productos')
@login_required
def productos():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))
    
    lista = Producto.query.all()
    return render_template('productos.html', productos=lista)

# Agregar producto
@main.route('/productos/agregar', methods=['GET', 'POST'])
@login_required
def agregar_producto():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))

    categorias = Categoria.query.all()

    if request.method == 'POST':
        nombre = request.form['nombre']
        categoria_id = request.form['categoria_id']
        precio = request.form['precio']
        stock = request.form['stock']
        stock_minimo = request.form['stock_minimo']

        nuevo = Producto(
            nombre=nombre,
            categoria_id=categoria_id,
            precio=precio,
            stock=stock,
            stock_minimo=stock_minimo
        )
        db.session.add(nuevo)
        db.session.commit()
        flash('Producto agregado correctamente')
        return redirect(url_for('main.productos'))

    return render_template('agregar_producto.html', categorias=categorias)


# Editar producto
@main.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    if current_user.rol != 'admin':
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))

    producto = Producto.query.get_or_404(id)
    categorias = Categoria.query.all()

    if request.method == 'POST':
        producto.nombre = request.form['nombre']
        producto.categoria_id = request.form['categoria_id']
        producto.precio = request.form['precio']
        producto.stock = request.form['stock']
        producto.stock_minimo = request.form['stock_minimo']

        db.session.commit()
        flash('Producto actualizado')
        return redirect(url_for('main.productos'))

    return render_template('editar_producto.html', producto=producto, categorias=categorias)


# Eliminar producto
@main.route('/productos/eliminar/<int:id>')
@login_required
def eliminar_producto(id):
    if current_user.rol != 'admin':
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))

    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado')
    return redirect(url_for('main.productos'))


@main.route('/ventas/registrar', methods=['GET', 'POST'])
@login_required
def registrar_venta():
    if current_user.rol not in ['admin', 'vendedor']:
        flash('Acceso no autorizado.')
        return redirect(url_for('main.dashboard'))

    productos = Producto.query.all()

    if request.method == 'POST':
        try:
            seleccionados = request.form.getlist('productos')
            detalles = []
            total = 0

            if not seleccionados:
                flash("Debes seleccionar al menos un producto.")
                return redirect(url_for('main.registrar_venta'))

            for id_str in seleccionados:
                id_producto = int(id_str)
                cantidad_raw = request.form.get(f'cantidad_{id_producto}', '').strip()

                if not cantidad_raw or not cantidad_raw.isdigit():
                    flash("Cantidad inválida.")
                    return redirect(url_for('main.registrar_venta'))

                cantidad = int(cantidad_raw)
                if cantidad <= 0:
                    flash("Cantidad debe ser mayor a cero.")
                    return redirect(url_for('main.registrar_venta'))

                producto = Producto.query.get(id_producto)
                if not producto:
                    flash("Producto no encontrado.")
                    return redirect(url_for('main.registrar_venta'))

                if producto.stock < cantidad:
                    flash(f"No hay suficiente stock para {producto.nombre}")
                    return redirect(url_for('main.registrar_venta'))

                subtotal = producto.precio * cantidad
                total += subtotal
                producto.stock -= cantidad

                detalle = DetalleVenta(
                    producto_id=id_producto,
                    cantidad=cantidad,
                    subtotal=subtotal
                )
                detalles.append(detalle)

            venta = Venta(usuario_id=current_user.id, total=total)
            db.session.add(venta)
            db.session.flush()

            for d in detalles:
                d.venta_id = venta.id
                db.session.add(d)

            db.session.commit()
            flash("✅ Venta registrada correctamente.")
            return redirect(url_for('main.dashboard'))

        except Exception as e:
            db.session.rollback()
            print("ERROR:", e)
            flash("❌ Error interno al procesar la venta.")
            return redirect(url_for('main.registrar_venta'))

    return render_template('registrar_venta.html', productos=productos)

@main.route('/ventas')
@login_required
def ventas():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))

    ventas = Venta.query.order_by(Venta.fecha.desc()).all()
    return render_template('ventas.html', ventas=ventas)

@main.route('/ventas/<int:id>')
@login_required
def detalle_venta(id):
    venta = Venta.query.get_or_404(id)

    # Si el usuario es vendedor y no es el dueño de la venta, se bloquea
    if current_user.rol == 'vendedor' and venta.usuario_id != current_user.id:
        flash("No tienes permiso para ver esta venta.")
        return redirect(url_for('main.dashboard'))

    detalles = DetalleVenta.query.filter_by(venta_id=id).all()
    vendedor = Usuario.query.get(venta.usuario_id)

    return render_template('detalle_venta.html', venta=venta, detalles=detalles, vendedor=vendedor)



@main.route('/reportes/ventas')
@login_required
def reporte_ventas():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))

    ventas_por_mes = db.session.query(
        extract('month', Venta.fecha).label('mes'),
        func.sum(Venta.total).label('total')
    ).group_by('mes').order_by('mes').all()

    meses = [f"Mes {int(v[0])}" for v in ventas_por_mes]  # etiquetas legibles
    totales = [float(v[1]) for v in ventas_por_mes]

    return render_template('reporte_ventas.html', meses=meses, totales=totales)

@main.route('/reportes/ventas_fecha', methods=['GET', 'POST'])
@login_required
def ventas_por_fecha():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))

    ventas = []
    total = 0
    fecha_inicio = ''
    fecha_fin = ''

    if request.method == 'POST':
        fecha_inicio = request.form['inicio']
        fecha_fin = request.form['fin']

        inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')

        ventas = Venta.query.filter(Venta.fecha.between(inicio_dt, fin_dt)).order_by(Venta.fecha).all()
        total = sum(float(v.total) for v in ventas)

    return render_template('ventas_fecha.html', ventas=ventas, total=total,
                           fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)

@main.route('/reportes/ventas_fecha/pdf', methods=['POST'])
@login_required
def exportar_ventas_pdf():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))

    fecha_inicio = request.form['inicio']
    fecha_fin = request.form['fin']

    inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')

    ventas = Venta.query.filter(Venta.fecha.between(inicio_dt, fin_dt)).order_by(Venta.fecha).all()
    total = sum(float(v.total) for v in ventas)

    html = render_template('ventas_pdf.html', ventas=ventas, total=total, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)

    if pisa_status.err:
        return "Error al generar el PDF", 500

    response = make_response(result.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=reporte_ventas.pdf'
    return response

@main.route('/compras/registrar', methods=['GET', 'POST'])
@login_required
def registrar_compra():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))

    productos = Producto.query.all()

    if request.method == 'POST':
        producto_id = int(request.form['producto_id'])
        cantidad = int(request.form['cantidad'])
        precio_unitario = float(request.form['precio_unitario'])
        total = cantidad * precio_unitario

        compra = Compra(
            producto_id=producto_id,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            total=total,
            usuario_id=current_user.id
        )
        db.session.add(compra)

        # Actualizar stock
        producto = Producto.query.get(producto_id)
        producto.stock += cantidad

        db.session.commit()
        flash('Compra registrada y stock actualizado')
        return redirect(url_for('main.dashboard'))

    return render_template('registrar_compra.html', productos=productos)


@main.route('/usuarios')
@login_required
def listar_usuarios():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))

    usuarios = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios, usuario=current_user)



@main.route('/usuarios/toggle/<int:id>', methods=['POST'])
@login_required
def cambiar_estado_usuario(id):
    if current_user.rol != 'admin':
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))

    usuario = Usuario.query.get_or_404(id)

    if usuario.id == current_user.id:
        flash('No puedes cambiar el estado de tu propio usuario.')
        return redirect(url_for('main.listar_usuarios'))

    usuario.estado = 'inactivo' if usuario.estado == 'activo' else 'activo'
    db.session.commit()
    flash(f"Usuario {'desactivado' if usuario.estado == 'inactivo' else 'activado'} correctamente.")
    return redirect(url_for('main.listar_usuarios'))

@main.route('/reportes/ventas_por_usuario')
@login_required
def ventas_por_usuario():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))

    resultados = db.session.query(
        Usuario.nombre,
        db.func.count(Venta.id).label('cantidad_ventas'),
        db.func.sum(Venta.total).label('total_ventas')
    ).join(Venta, Venta.usuario_id == Usuario.id) \
     .group_by(Usuario.id) \
     .all()

    return render_template('ventas_por_usuario.html', resultados=resultados)

@main.route('/reportes/ventas_por_usuario/pdf')
@login_required
def ventas_por_usuario_pdf():
    if current_user.rol != 'admin':
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))

    resultados = db.session.query(
        Usuario.nombre,
        db.func.count(Venta.id).label('cantidad_ventas'),
        db.func.sum(Venta.total).label('total_ventas')
    ).join(Venta, Venta.usuario_id == Usuario.id) \
     .group_by(Usuario.id) \
     .all()

    fecha_actual = datetime.now()

    # HTML para el PDF, pasando la fecha actual
    html = render_template('ventas_por_usuario_pdf.html', resultados=resultados, fecha_actual=fecha_actual)

    # Convertir HTML a PDF
    pdf = BytesIO()
    pisa.CreatePDF(html, dest=pdf)
    pdf.seek(0)

    response = make_response(pdf.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename="ventas_por_usuario.pdf"'
    return response

    return make_response(pdf.read(), {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename="ventas_por_usuario.pdf"'
    })

@main.route('/ventas/<int:id>/pdf')
@login_required
def factura_pdf(id):
    venta = Venta.query.get_or_404(id)
    detalles = DetalleVenta.query.filter_by(venta_id=id).all()
    vendedor = Usuario.query.get(venta.usuario_id)
    html = render_template('factura_pdf.html', venta=venta, detalles=detalles, vendedor=vendedor)

    pdf = BytesIO()
    pisa.CreatePDF(html, dest=pdf)
    pdf.seek(0)

    return make_response(pdf.read(), {
        'Content-Type': 'application/pdf',
        'Content-Disposition': f'attachment; filename=factura_venta_{venta.id}.pdf'
    })

@main.route('/productos/buscar', methods=['GET'])
@login_required
def buscar_productos():
    if current_user.rol not in ['vendedor', 'admin']:
        flash('Acceso no autorizado')
        return redirect(url_for('main.dashboard'))

    nombre = request.args.get('nombre', '').strip()
    categoria_id = request.args.get('categoria', '')

    query = Producto.query

    if nombre:
        query = query.filter(Producto.nombre.ilike(f'%{nombre}%'))

    if categoria_id and categoria_id.isdigit():
        query = query.filter_by(categoria_id=int(categoria_id))

    productos = query.all()
    categorias = Categoria.query.all()

    return render_template('buscar_productos.html', productos=productos, categorias=categorias, nombre=nombre, categoria_id=categoria_id)

@main.route('/mis_ventas')
@login_required
def mis_ventas():
    if current_user.rol != 'vendedor':
        flash("Acceso no autorizado.")
        return redirect(url_for('main.dashboard'))

    ventas = Venta.query.filter_by(usuario_id=current_user.id).order_by(Venta.fecha.desc()).all()
    return render_template('mis_ventas.html', ventas=ventas)

@main.route('/stock/alertas')
@login_required
def alertas_stock():
    if current_user.rol not in ['admin', 'vendedor']:
        flash("Acceso no autorizado.")
        return redirect(url_for('main.dashboard'))

    margen = 2  # Puedes ajustar este margen según tu necesidad
    productos = Producto.query.filter(
        (Producto.stock <= (Producto.stock_minimo + margen))
    ).all()
    return render_template('alertas_stock.html', productos=productos)

@main.route('/mi_perfil')
@login_required
def mi_perfil():
    return render_template('perfil.html', usuario=current_user)

@main.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    if request.method == 'POST':
        current_user.nombre = request.form['nombre']
        current_user.telefono = request.form['telefono']
        current_user.direccion = request.form['direccion']
        db.session.commit()
        flash('Perfil actualizado correctamente.')
        return redirect(url_for('main.mi_perfil'))

    return render_template('editar_perfil.html', usuario=current_user)

@main.route('/perfil/contraseña', methods=['GET', 'POST'])
@login_required
def cambiar_contraseña():
    if request.method == 'POST':
        actual = request.form['actual']
        nueva = request.form['nueva']
        confirmar = request.form['confirmar']

        if not check_password_hash(current_user.contraseña, actual):
            flash('Contraseña actual incorrecta.')
        elif nueva != confirmar:
            flash('La nueva contraseña no coincide.')
        else:
            current_user.contraseña = generate_password_hash(nueva)
            db.session.commit()
            flash('Contraseña actualizada exitosamente.')
            return redirect(url_for('main.mi_perfil'))

    return render_template('cambiar_contraseña.html')

@main.route('/reporte/general')
@login_required
def reporte_general():


    hoy = datetime.now()
    inicio_mes = datetime(hoy.year, hoy.month, 1)
    seis_meses_atras = hoy - timedelta(days=180)

    # 1. Top 5 productos más vendidos
    top_productos = (
        db.session.query(Producto.nombre, func.sum(DetalleVenta.cantidad).label('total'))
        .join(DetalleVenta)
        .join(Venta)
        .filter(Venta.fecha >= inicio_mes)
        .group_by(Producto.id)
        .order_by(func.sum(DetalleVenta.cantidad).desc())
        .limit(5)
        .all()
    )

    nombres_top = [r[0] for r in top_productos]
    cantidades_top = [int(r[1]) for r in top_productos]

    # 2. Total de ventas por mes (últimos 6 meses)
    ventas_mensuales = (
        db.session.query(func.date_format(Venta.fecha, "%Y-%m").label("mes"), func.sum(Venta.total))
        .filter(Venta.fecha >= seis_meses_atras)
        .group_by("mes")
        .order_by("mes")
        .all()
    )
    meses = [r[0] for r in ventas_mensuales]
    totales = [float(r[1]) for r in ventas_mensuales]

    # 3. Ventas por categoría
    ventas_categoria = (
        db.session.query(Categoria.nombre, func.sum(DetalleVenta.subtotal))
        .join(Producto, Categoria.id == Producto.categoria_id)
        .join(DetalleVenta, Producto.id == DetalleVenta.producto_id)
        .join(Venta)
        .filter(Venta.fecha >= inicio_mes)
        .group_by(Categoria.id)
        .all()
    )
    categorias = [r[0] for r in ventas_categoria]
    totales_categoria = [float(r[1]) for r in ventas_categoria]

    return render_template(
        'reporte_general.html',
        nombres_top=nombres_top,
        cantidades_top=cantidades_top,
        meses=meses,
        totales=totales,
        categorias=categorias,
        totales_categoria=totales_categoria
    )

