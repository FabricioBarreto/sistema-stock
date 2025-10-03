from . import db
from flask_login import UserMixin


class Usuario(db.Model, UserMixin):
    """Modelo de usuario del sistema."""

    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cedula = db.Column(db.String(20), unique=True, nullable=True)
    correo = db.Column(db.String(100), unique=True, nullable=True, index=True)
    password = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False)
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(100))
    estado = db.Column(db.String(20), default="activo")
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp())
    username = db.Column(db.String(50), unique=True, nullable=False)

    ventas = db.relationship(
        "Venta", back_populates="vendedor", cascade="all, delete-orphan"
    )
    compras = db.relationship(
        "Compra", back_populates="usuario", cascade="all, delete-orphan"
    )


class Categoria(db.Model):
    """Modelo de categoría de productos."""

    __tablename__ = "categorias"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)

    productos = db.relationship(
        "Producto", back_populates="categoria", cascade="all, delete-orphan"
    )


class Producto(db.Model):
    """Modelo de producto."""

    __tablename__ = "productos"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    stock_minimo = db.Column(db.Integer, nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=False)

    categoria = db.relationship("Categoria", back_populates="productos")
    detalles = db.relationship(
        "DetalleVenta", back_populates="producto", cascade="all, delete-orphan"
    )
    compras = db.relationship(
        "Compra", back_populates="producto", cascade="all, delete-orphan"
    )


class Venta(db.Model):
    """Modelo de venta."""

    __tablename__ = "ventas"
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=db.func.current_timestamp())
    total = db.Column(db.Numeric(10, 2), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    vendedor = db.relationship("Usuario", back_populates="ventas")
    detalles = db.relationship(
        "DetalleVenta", back_populates="venta", cascade="all, delete-orphan"
    )


class DetalleVenta(db.Model):
    """Detalle de cada producto vendido en una venta."""

    __tablename__ = "detalle_venta"
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey("ventas.id"), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

    venta = db.relationship("Venta", back_populates="detalles")
    producto = db.relationship("Producto", back_populates="detalles")


class Compra(db.Model):
    """Modelo de compra de productos para stock."""

    __tablename__ = "compras"
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    fecha = db.Column(db.DateTime, default=db.func.current_timestamp())
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    producto = db.relationship("Producto", back_populates="compras")
    usuario = db.relationship("Usuario", back_populates="compras")
