"""
Generator raportów PDF z postępów ucznia
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime


class ReportGenerator:
    def __init__(self, student_name: str, stats_data: dict):
        self.student_name = student_name
        self.stats_data = stats_data
        self.filename = f"raport_{student_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
    def generate_report(self):
        """Generuje raport PDF"""
        doc = SimpleDocTemplate(
            self.filename,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        
        # Kontener na elementy
        elements = []
        styles = getSampleStyleSheet()
        
        # Tytuł
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4')
        )
        
        elements.append(Paragraph(f"Raport postępów - {self.student_name}", title_style))
        elements.append(Spacer(1, 12))
        
        # Data
        elements.append(
            Paragraph(
                f"Data wygenerowania: {datetime.now().strftime('%d.%m.%Y')}",
                styles['Normal']
            )
        )
        elements.append(Spacer(1, 20))
        
        # Statystyki ogólne
        elements.append(Paragraph("Podsumowanie", styles['Heading2']))
        
        summary_data = [
            ['Wskaźnik', 'Wartość'],
            ['Liczba sesji', str(self.stats_data['total_sessions'])],
            ['Łączna liczba zadań', str(self.stats_data['total_questions'])],
            ['Poprawne odpowiedzi', str(self.stats_data['total_correct'])],
            ['Skuteczność', f"{self._calculate_accuracy():.1f}%"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        
        # Wyniki według tematów
        if self.stats_data['topics_performance']:
            elements.append(Paragraph("Wyniki według tematów", styles['Heading2']))
            
            topics_data = [['Temat', 'Zadania', 'Poprawne', 'Skuteczność']]
            
            for topic, stats in self.stats_data['topics_performance'].items():
                accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
                topics_data.append([
                    topic.capitalize(),
                    str(stats['total']),
                    str(stats['correct']),
                    f"{accuracy:.1f}%"
                ])
                
            topics_table = Table(topics_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            topics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            elements.append(topics_table)
            
        # Buduj PDF
        doc.build(elements)
        return self.filename
        
    def _calculate_accuracy(self):
        """Oblicza ogólną skuteczność"""
        if self.stats_data['total_questions'] == 0:
            return 0
        return (self.stats_data['total_correct'] / self.stats_data['total_questions']) * 100