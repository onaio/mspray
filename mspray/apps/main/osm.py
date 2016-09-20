from datetime import datetime
from django.contrib.gis.geos import LineString
from django.contrib.gis.geos import Point
from django.contrib.gis.geos import Polygon
from lxml import etree

from mspray.apps.main.models import Node, Way


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
            geom = LineString(points)

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


def get_date(string_date):
    if string_date:
        return datetime.strptime(string_date, '%Y-%m-%dT%H:%M:%SZ')

    return None


def get_nodes(osm_xml):
    root = _get_xml_obj(osm_xml)

    nodes = []
    for node in root.findall('node'):
        id = node.get('id')
        tags = {
            tag.get('k'): tag.get('v')
            for tag in node.findall('tag')
        }
        x, y = float(node.get('lon')), float(node.get('lat'))
        point = Point(x, y)
        if not id.startswith("-"):
            nodes.append({
                'node_id': int(id),
                'point': point,
                'version': int(node.get('version', 0)),
                'changeset': int(node.get('changeset', 0)),
                'timestamp': get_date(node.get('timestamp')),
                'user': tags,
            })

    return nodes


def add_node(node):
    node_id = node.get('node_id')
    version = node.get('version')
    changeset = node.get('changeset')
    user = node.get('user')
    timestamp = node.get('timestamp')
    point = node.get('point')
    tags = node.get('tags')

    obj, created = Node.objects.update_or_create(
        node_id=node_id,
        geom=point,
        defaults={
            'version': version,
            'changeset': changeset,
            'user': user,
            'timestamp': timestamp,
            'tags': tags})

    return obj


def add_way(way):
    way_id = way.get('id')
    action = way.get('action')
    version = way.get('version')
    changeset = way.get('changeset')
    user = way.get('user')
    tags = way.get('tags')
    timestamp = way.get('timestamp')
    geom = way.get('geom')

    obj, created = Way.objects.update_or_create(
        way_id=way_id,
        defaults={
            'action': action,
            'version': version,
            'changeset': changeset,
            'user': user,
            'timestamp': timestamp,
            'geom': geom,
            'tags': tags
        })

    return obj


def get_way_geom(nd_list, root):
    if len(nd_list) == 0:
        return

    points = []
    for nd in nd_list:
        points.append(_get_node(nd.get('ref'), root))

    try:
        return Polygon(points)
    except:
        return LineString(points)


def get_ways(osm_xml):
    root = _get_xml_obj(osm_xml)
    ways = []
    for way in root.findall('way'):
        id = way.get('id')
        action = way.get('action')
        version = int(way.get('version', 0))
        changeset = int(way.get('changeset', 0))
        timestamp = get_date(way.get('timestamp'))
        user = way.get('user')
        if not id.startswith("-"):
            geom = get_way_geom(way.findall('nd'), root)

            tags = {
                tag.get('k'): tag.get('v')
                for tag in way.findall('tag')
            }

            ways.append({
                'id': id,
                'geom': geom,
                'tags': tags,
                'action': action,
                'version': version,
                'changeset': changeset,
                'timestamp': timestamp,
                'user': user
            })

    return ways


def get_osm_xml(osm_file):
    with open(osm_file) as osm_file:
        osm_xml = osm_file.read().strip()

        return osm_xml


def add_or_update_osm_data(osm_file):
    osm_xml = get_osm_xml(osm_file)

    ways = get_ways(osm_xml)
    nodes = get_nodes(osm_xml)

    for way in ways:
        add_way(way)

    for node in nodes:
        add_node(node)


def generate_osm_xml(osm_list):
    xml = u""
    if (len(osm_list) and isinstance(osm_list, list)):
        root = etree.Element(
            "osm", version='0.6', generator='osmconvert 0.8.5'
        )

        nodes = []
        for a in osm_list:
            tags = a.get('tags')
            geom = a.get('geom')
            node_ids = []
            if geom:
                coordinates = geom.get('coordinates')[0]
                for coordinate in coordinates:
                    point = Point(coordinate)
                    nd = Node.objects.filter(geom=point).first()
                    if nd:
                        node_ids.append(nd.node_id)
                        nodes.append(nd)

            # create a dict with way tag attributes
            kwargs = {}
            for k, v in a.items():
                if k not in ['tags', 'geom', 'id'] and v is not None:
                    kwargs['id' if k == 'way_id' else k] = str(v)

            # create way tag
            way_tag = etree.Element("way", **kwargs)

            # add nd tags to way tag if they exist
            if len(node_ids) != 0:
                for nd in node_ids:
                    etree.SubElement(way_tag, "nd", ref=str(nd))

            # add tag tags to way tag if they exist
            if tags:
                for k, v in tags.items():
                    etree.SubElement(way_tag, "tag", k=str(k), v=str(v))

            root.append(way_tag)

        # create node tags
        if nodes:
            for node in nodes:
                node_tag = etree.Element("node", id=str(node.node_id))
                root.append(node_tag)

        xml = etree.tostring(root, encoding='utf-8', xml_declaration=True)

    return xml
