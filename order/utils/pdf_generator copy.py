from django.template.loader import render_to_string
from django.http import HttpResponse
from io import BytesIO
import math
from num2words import num2words
from django.conf import settings
from django.template.loader import get_template

# Install this library: pip install xhtml2pdf
from xhtml2pdf import pisa 

# --- Minimal Invoice Generator using HTML/xhtml2pdf ---

class InvoicePDFGenerator:
    """Generate PDF invoices for orders using an HTML template and xhtml2pdf."""

    def __init__(self, order):
        self.order = order
        self.gst_rate = getattr(self.order, 'gst_amount', 0)
        
        # --- Calculations (Same as before) ---
        self.subtotal = sum(item.quantity * item.price for item in self.order.items.all())
        
        cgst_rate = self.gst_rate / 2
        sgst_rate = self.gst_rate / 2
        
        self.total_cgst_amt = sum(
            (item.quantity * item.price * cgst_rate) / 100
            for item in self.order.items.all()
        )
        self.total_sgst_amt = sum(
            (item.quantity * item.price * sgst_rate) / 100
            for item in self.order.items.all()
        )
        
        self.final_total_before_round = self.subtotal + self.total_cgst_amt + self.total_sgst_amt
        
        total_base = getattr(self.order, 'total_amount', self.final_total_before_round)
        
        self.rounded_amount = math.ceil(total_base)
        self.round_off = self.rounded_amount - total_base
        
        try:
            self.amount_words = num2words(int(self.rounded_amount), lang='en_IN').title() + " Only"
        except:
            self.amount_words = "Amount unavailable"


    def _get_html_context(self):
        """Prepare data context for the HTML template."""
        
        cgst_rate = self.gst_rate / 2
        
        item_data = []
        for idx, item in enumerate(self.order.items.all(), 1):
            item_total = item.quantity * item.price
            cgst_amount = (item_total * cgst_rate) / 100
            sgst_amount = (item_total * cgst_rate) / 100 # SGST rate is also cgst_rate
            
            item_data.append({
                'no': idx,
                'name': item.product.name,
                'hsn_code': getattr(item.product, 'hsn_code', '') or 'N/A',
                'quantity': item.quantity,
                'price': item.price,
                'taxable_amount': item_total,
                'cgst_rate': cgst_rate,
                'cgst_amount': cgst_amount,
                'sgst_rate': cgst_rate,
                'sgst_amount': sgst_amount,
                'total': item_total + cgst_amount + sgst_amount,
            })

        return {
            'order': self.order,
            'items': item_data,
            'subtotal': self.subtotal,
            'total_cgst_amt': self.total_cgst_amt,
            'total_sgst_amt': self.total_sgst_amt,
            'final_total_before_round': self.final_total_before_round,
            'rounded_amount': self.rounded_amount,
            'round_off': self.round_off,
            'amount_words': self.amount_words,
        }

    def generate(self):
        """Render the HTML template and convert it to a PDF byte string using xhtml2pdf."""
        
        context = self._get_html_context()
        html = render_to_string('invoice.html', context)
        result_file = BytesIO()

        # The core xhtml2pdf conversion function
        pisa_status = pisa.pisaDocument(
            BytesIO(html.encode("UTF-8")), # Convert HTML string to bytes
            dest=result_file,
            encoding='UTF-8'
        )

        if pisa_status.err:
            raise Exception("Error generating PDF with xhtml2pdf: Check HTML/CSS validity.")
            
        return result_file.getvalue()

    def get_http_response(self, filename=None):
        """Generate PDF and return as Django HttpResponse."""
        pdf = self.generate()
        
        if not filename:
            filename = f"invoice_{self.order.invoice_number}.pdf"
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"' 
        
        return response