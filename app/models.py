from . import db
from flask_login import UserMixin

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contraseña = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False)
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(100))
    estado = db.Column(db.String(20), default='activo')
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp())

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    stock_minimo = db.Column(db.Integer, nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'))

    categoria = db.relationship('Categoria', backref='productos')


class Venta(db.Model):
    __tablename__ = 'ventas'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=db.func.current_timestamp())
    total = db.Column(db.Numeric(10, 2))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    vendedor = db.relationship('Usuario', backref='ventas')


class DetalleVenta(db.Model):
    __tablename__ = 'detalle_venta'
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('ventas.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

    producto = db.relationship('Producto', backref='detalles')

class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)


class Compra(db.Model):
    __tablename__ = 'compras'
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2))
    total = db.Column(db.Numeric(10, 2))
    fecha = db.Column(db.DateTime, default=db.func.current_timestamp())
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))

    producto = db.relationship('Producto')
    usuario = db.relationship('Usuario')


