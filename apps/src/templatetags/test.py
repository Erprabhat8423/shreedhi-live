from django import template
#from ...developer_console.models import EntityType

register = template.Library()

#@register.simple_tag
# def entity_count(id):
#     product = EntityType.objects.get(id=id)
#     return product.entity_type