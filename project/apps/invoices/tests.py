from apps.invoices.views import covert_number_to_string
from django.test import TestCase

class TestCovertNumberToString(TestCase):
    @classmethod
    def setUp(self):
        self.number_1 = 8012900000
        self.number_2 = 99012900000
        self.number_3 = 199012900000
        self.number_4 = 1770000
        self.number_5 = 560000
        self.number_6 = 36000000
        self.number_7 = 955555000
        self.number_8 = 444000
        self.number_9 = 999999990000
        self.number_10 = 101000

    def test_case_1(self):
        result = covert_number_to_string(self.number_1)
        self.assertEqual(result, "  tám tỷ   mười hai triệu chín trăm nghìn đồng")

    def test_case_2(self):
        result = covert_number_to_string(self.number_2)
        self.assertEqual(result, "  chín mươi chín tỷ   mười hai triệu chín trăm nghìn đồng")

    def test_case_3(self):
        result = covert_number_to_string(self.number_3)
        self.assertEqual(result, " một trăm chín mươi chín tỷ   mười hai triệu chín trăm nghìn đồng")

    def test_case_4(self):
        result = covert_number_to_string(self.number_4)
        self.assertEqual(result, "   một triệu bảy trăm bảy mươi nghìn đồng")

    def test_case_5(self):
        result = covert_number_to_string(self.number_5)
        self.assertEqual(result, " năm trăm sáu mươi nghìn đồng")

    def test_case_6(self):
        result = covert_number_to_string(self.number_6)
        self.assertEqual(result, "   ba mươi sáu triệu đồng")

    def test_case_7(self):
        result = covert_number_to_string(self.number_7)
        self.assertEqual(result, "  chín trăm năm mươi lăm triệu năm trăm năm mươi lăm nghìn đồng")

    def test_case_8(self):
        result = covert_number_to_string(self.number_8)
        self.assertEqual(result, " bốn trăm bốn mươi bốn nghìn đồng")

    def test_case_9(self):
        result = covert_number_to_string(self.number_9)
        self.assertEqual(result, " chín trăm chín mươi chín tỷ  chín trăm chín mươi chín triệu chín trăm chín mươi nghìn đồng")

    def test_case_10(self):
        result = covert_number_to_string(self.number_10)
        self.assertEqual(result, " một trăm lẻ một nghìn đồng")
