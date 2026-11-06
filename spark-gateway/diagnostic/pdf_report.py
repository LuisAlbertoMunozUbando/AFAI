import re
from datetime import datetime
from zoneinfo import ZoneInfo
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from .pipeline import CATALOG

FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
if Path(FONT).exists():
    pdfmetrics.registerFont(TTFont('AFAI', FONT))
    pdfmetrics.registerFont(TTFont('AFAI-Bold', FONT.replace('.ttf','-Bold.ttf')))
    pdfmetrics.registerFontFamily('AFAI',normal='AFAI',bold='AFAI-Bold',italic='AFAI',boldItalic='AFAI-Bold')
BASE='AFAI' if Path(FONT).exists() else 'Helvetica'
BOLD='AFAI-Bold' if BASE=='AFAI' else 'Helvetica-Bold'

def filename(payload, job):
    name=payload.email or payload.company
    name=re.sub(r'[^\w.@+-]', '_', name, flags=re.UNICODE)[:160].strip('._') or 'diagnostico'
    day=datetime.now(ZoneInfo('America/Monterrey')).strftime('%Y-%m-%d')
    return f'{name}_{day}_{job[:8]}.pdf'

def render(path,payload,report,review,model,job):
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BodyA',fontName=BASE,fontSize=10,leading=15,textColor=colors.HexColor('#243643'),spaceAfter=9,wordWrap='CJK'))
    styles.add(ParagraphStyle(name='TitleA',fontName=BOLD,fontSize=31,leading=38,textColor=colors.HexColor('#10251c'),spaceAfter=20))
    styles.add(ParagraphStyle(name='HeadingA',fontName=BOLD,fontSize=15,leading=21,textColor=colors.HexColor('#27601e'),spaceBefore=17,spaceAfter=10,keepWithNext=True))
    styles.add(ParagraphStyle(name='SmallA',fontName=BASE,fontSize=8,leading=12,textColor=colors.HexColor('#52626c'),spaceAfter=8,wordWrap='CJK'))
    def para(text,style='BodyA'): return Paragraph(escape(str(text)).replace('\n','<br/>'),styles[style])
    story=[]
    def section(title,text):
        story.append(para(title,'HeadingA'))
        for line in text.split('\n'):
            if line.strip(): story.append(para(line))
    def bullets(title,items):
        story.append(para(title,'HeadingA'))
        for i,item in enumerate(items,1): story.append(para(f'{i}. {item}'))
    story += [Spacer(1,28),para('AFAI / AUTOMATION BRIEF','SmallA'),
              para('Tu siguiente paso\nhacia la automatización','TitleA'),
              para(payload.company,'HeadingA'),para(payload.industry),
              para('Diagnóstico preliminar generado con IA · '+datetime.now(ZoneInfo('America/Monterrey')).strftime('%d/%m/%Y'))]
    section('Una oportunidad concreta',report.summary)
    section('Tu pitch, más claro',report.improved_pitch)
    story.append(para('Este documento propone un punto de partida. No es una cotización ni una validación de ingeniería. AFAI es un proyecto independiente y no representa a NVIDIA.','SmallA'))
    story.append(PageBreak())
    bullets('01 / Ajustes al planteamiento',report.corrections)
    bullets('02 / Información que falta',report.missing_information)
    section('03 / Arquitectura propuesta',report.architecture)
    story.append(para('04 / Herramientas NVIDIA con propósito','HeadingA'))
    cat={x['id']:x for x in CATALOG}
    if not report.tools: story.append(para('No se justifica una herramienta NVIDIA específica con los datos proporcionados.'))
    for item in report.tools:
        tool=cat[item.id]
        story.extend([para(tool['name'],'HeadingA'),para(item.why),para('Validación requerida: '+item.validation),
            Paragraph('<link href="'+escape(tool['url'])+'" color="#27601e">'+escape(tool['url'])+'</link>',styles['SmallA']),
            para('Referencia de catálogo revisada: '+tool['checked']+'. Confirmar requisitos y licencias vigentes.','SmallA')])
    bullets('05 / Piloto propuesto',report.pilot_plan)
    bullets('06 / Cómo medir el resultado',report.metrics)
    bullets('07 / Riesgos y límites',report.risks)
    section('08 / Segunda revisión del borrador',review)
    story.append(PageBreak())
    section('Anexo / Información proporcionada por el visitante',payload.process)
    section('Objetivo',payload.goal)
    section('Pitch original',payload.pitch)
    if payload.constraints: section('Restricciones',payload.constraints)
    section('Trazabilidad',f'ID: {job}\nModelo local: {model}\nRecursos usados: inferencia Spark (revisión, propuesta y auditoría), catálogo NVIDIA y generación PDF.\nNo se ejecutaron simulaciones, análisis de video ni acciones físicas. La auditoría utiliza el mismo modelo, no un experto independiente.')
    story.append(para('El correo opcional se usa para nombrar el archivo; no se envían emails ni se activa marketing. Se conserva una copia privada para AFAI. Solicitudes de eliminación: luisalbertomunozubando@gmail.com, indicando el ID del informe.','SmallA'))
    def page(canvas,doc):
        canvas.saveState()
        w,h=doc.pagesize
        canvas.setFillColor(colors.HexColor('#13231d'));canvas.rect(0,h-32,w,32,fill=1,stroke=0)
        canvas.setFont(BOLD,9);canvas.setFillColor(colors.HexColor('#a3e635'));canvas.drawString(44,h-21,'AUTOMATION FOUNDRY AI')
        canvas.setStrokeColor(colors.HexColor('#c6d5cc'));canvas.line(44,39,w-44,39)
        canvas.setFillColor(colors.HexColor('#52626c'));canvas.setFont(BASE,8)
        canvas.drawString(44,25,'Diagnóstico preliminar · '+job[:8]);canvas.drawRightString(w-44,25,str(doc.page))
        canvas.restoreState()
    SimpleDocTemplate(str(path),rightMargin=44,leftMargin=44,topMargin=53,bottomMargin=54,
        title='AFAI - Diagnóstico de automatización',author='Automation Foundry AI').build(story,onFirstPage=page,onLaterPages=page)
