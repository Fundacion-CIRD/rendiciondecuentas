from .models import ItemCompra, Concepto


def total_por_concepto():
    items = ItemCompra.objects.all()
    conceptos = {}
    for item in items:
        if item.concepto.padre:
            concepto = item.concepto.padre.nombre
        else:
            concepto = item.concepto.nombre
        try:
            conceptos[concepto] += item.precio_total_pyg
        except KeyError:
            conceptos[concepto] = item.precio_total_pyg
    return conceptos
