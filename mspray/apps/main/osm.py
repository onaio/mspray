from django.contrib.gis.geos import LineString
from django.contrib.gis.geos import Point
from django.contrib.gis.geos import Polygon
from lxml import etree

from mspray.apps.main.models.household import Household


def _get_xml_obj(xml):
    if not isinstance(xml, bytes):
        xml = xml.strip().encode()
    try:
        return etree.fromstring(xml)
    except etree.XMLSyntaxError as e:
        if 'Attribute action redefined' in e.msg:
            xml = xml.replace(b'action="modify" ', b'')

            return _get_xml_obj(xml)


def _get_node(ref, root):
    point = None
    nodes = root.xpath('//node[@id="{}"]'.format(ref))
    if nodes:
        node = nodes[0]
        x, y = float(node.get('lon')), float(node.get('lat'))
        point = Point(x, y)

    return point


def parse_osm_ways(osm_xml, include_osm_id=False):
    """Converts an OSM XMl to a list of GEOSGeometry objects """
    items = []

    root = _get_xml_obj(osm_xml)

    for way in root.findall('way'):
        geom = None
        points = []
        for nd in way.findall('nd'):
            points.append(_get_node(nd.get('ref'), root))
        try:
            geom = Polygon(points)
        except:
            try:
                geom = LineString(points)
            except Exception as e:
                print(way.values())
                pass

        if geom:
            tags = parse_osm_tags(way, include_osm_id)
            items.append({
                'osm_id': way.get('id'),
                'geom': geom,
                'tags': tags,
                'osm_type': 'way'
            })

    return items


def parse_osm_nodes(osm_xml, include_osm_id=False):
    """Converts an OSM XMl to a list of GEOSGeometry objects """
    items = []

    root = _get_xml_obj(osm_xml)

    for node in root.findall('node'):
        x, y = float(node.get('lon')), float(node.get('lat'))
        point = Point(x, y)
        tags = parse_osm_tags(node, include_osm_id)
        items.append({
            'osm_id': node.get('id'),
            'geom': point,
            'tags': tags,
            'osm_type': 'node'
        })

    return items


def parse_osm_tags(node, include_osm_id=False):
    """Retrieves all the tags from a osm xml node"""
    tags = {} if not include_osm_id else {node.tag + ':id': node.get('id')}
    for tag in node.findall('tag'):
        key, val = tag.attrib['k'], tag.attrib['v']
        if val == '' or val.upper() == 'FIXME':
            continue
        tags.update({key: val})

    return tags


def parse_osm(osm_xml, include_osm_id=False):
    result = []
    ways = parse_osm_ways(osm_xml, include_osm_id)
    result.extend(ways)
    nodes = parse_osm_nodes(osm_xml, include_osm_id)
    result.extend(nodes)

    return result


def clean_osm_file_with_db(osm_file, output_file):
    """
    Goes through the provided XML and removes any structures
    that do not exist in the Database as Household objects
    Writes the result in the output_file
    """
    with open(osm_file) as f:
        osm_xml = f.read()
    root = _get_xml_obj(osm_xml.strip())
    removed = 0
    if root is not None:
        structures = root.findall('way')
        for structure in structures:
            try:
                osmid = structure.attrib['id']
            except KeyError:
                # no OSM ID, remove this structure
                structure.getparent().remove(structure)
                removed += 1
            else:
                if not Household.objects.filter(hh_id=int(osmid)).exists():
                    # remove this structure because it is not in our DB
                    structure.getparent().remove(structure)
                    removed += 1
        # write to file
        tree = etree.ElementTree(root)
        tree.write(output_file, pretty_print=True, xml_declaration=True,
                   encoding="utf-8")
    return removed
