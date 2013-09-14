from cyder.cydhcp.network.models import Network
from cyder.cydhcp.range.models import Range


def pretty_networks(networks):
    return [network.network_str for network in networks]


def get_vrfs(networks):
    vrfs = set()
    if len(networks) > 0:
        for network in networks:
            vrfs.update(network.vrf)
    return vrfs


def get_ranges(networks, ctnr=None, range_types=['st', 'dy']):
    ranges = set()
    if len(networks) > 0:
        for network in networks:
            if ctnr and ctnr.name != 'global':
                ranges.update(Range.objects.filter(
                    network_id=network.id, cntr__id=ctnr.id,
                    range_type__in=range_types))
            else:
                ranges.update(Range.objects.filter(
                    network_id=network.id, range_type__in=range_types))

    return ranges


def calc_networks(network):
    network.update_network()
    eldars = []
    sub_networks = []
    for pnet in Network.objects.all():
        pnet.update_network()
        if pnet.pk == network.pk:
            continue
        if pnet.network.overlaps(network.network):
            if pnet.prefixlen > network.prefixlen:
                sub_networks.append(pnet)
            else:
                eldars.append(pnet)
    return eldars, sub_networks


def calc_parent(network):
    eldars, sub_net = calc_networks(network)
    if not eldars:
        # Why!?! stupid.
        return []
    parent = sorted(eldars, key=lambda n: n.prefixlen, reverse=True)[0]
    return parent


def calc_parent_str(network_str, ip_type):
    network = Network(network_str=network_str, ip_type=ip_type)
    return calc_parent(network)
