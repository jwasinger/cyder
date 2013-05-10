ACTION_CREATE = 0
ACTION_VIEW = 1
ACTION_UPDATE = 2
ACTION_DELETE = 3
ACTIONS = {
    ACTION_CREATE: 'Create',
    ACTION_VIEW: 'View',
    ACTION_UPDATE: 'Update',
    ACTION_DELETE: 'Delete',
}

LEVEL_GUEST = 0
LEVEL_USER = 1
LEVEL_ADMIN = 2
LEVELS = {
    LEVEL_GUEST: 'Guest',
    LEVEL_USER: 'User',
    LEVEL_ADMIN: 'Admin',
}

IP_TYPE_4 = '4'
IP_TYPE_6 = '6'
IP_TYPES = {
    IP_TYPE_4: 'ipv4',
    IP_TYPE_6: 'ipv6'
}

DHCP_OBJECTS = ("workgroup", "vrf", "vlan", "site", "range", "network",
                "static_interface", "dynamic_interface",)

DNS_OBJECTS = ("address_record", "cname", "domain", "mx", "nameserver", "ptr",
               "soa", "srv", "sshfp", "txt", "view",)

CORE_OBJECTS = ("ctnr_users", "ctnr", "user",)
