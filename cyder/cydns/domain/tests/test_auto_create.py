from django.core.exceptions import ValidationError
from django.test import TestCase

from cyder.cydns.domain.models import Domain
from cyder.cydns.utils import ensure_label_domain
from cyder.cydns.soa.models import SOA


class AutoCreateTests(TestCase):
    """These tests should cover zone insurance and delegation blocking.
    Purgeable Domains
    """

    def test_delegation_block(self):
        c = Domain(name='com')
        c.save()
        s, _ = SOA.objects.get_or_create(primary="foo", contact="Foo",
                                         root_domain=c, description="foo")
        self.assertFalse(c.purgeable)
        f_c = Domain(name='foo.com')
        f_c.delegated = True
        f_c.save()
        self.assertFalse(f_c.purgeable)
        self.assertTrue(f_c.delegated)

        fqdn = "z.baz.foo.com"
        self.assertRaises(ValidationError, ensure_label_domain, fqdn)

    def test_no_soa_block(self):
        fqdn = "baz.bar.foo.eu"
        self.assertRaises(ValidationError, ensure_label_domain, fqdn)
        c = Domain(name='eu')
        c.save()
        self.assertFalse(c.purgeable)
        f_c = Domain(name='foo.eu')
        f_c.save()
        self.assertFalse(f_c.purgeable)

        # Even with domains there, they aren't part of a zone and should so
        # creation should fail.
        self.assertRaises(ValidationError, ensure_label_domain, fqdn)

    def test_no_soa_block2(self):
        c = Domain(name='moo')
        c.save()
        f_c = Domain(name='foo.moo')
        f_c.save()
        s, _ = SOA.objects.get_or_create(primary="bar23", contact="Foo",
                                         root_domain=f_c, description="bar")

        self.assertRaises(ValidationError, ensure_label_domain, "baz.moo")
