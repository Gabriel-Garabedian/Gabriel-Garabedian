"""Render self-contained profile cards; --refresh fetches the public calendar."""
import base64
from collections import defaultdict
from datetime import date, timedelta
from html import escape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BLUE, INK, PAPER = '#244ce4', '#24251f', '#f8f7f2'

class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells, self.counts = {}, {}
        self.target, self.parts = None, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('data-date') and a.get('id'):
            self.cells[a['id']] = a['data-date']
        if tag == 'tool-tip':
            self.target, self.parts = a.get('for'), []

    def handle_data(self, data):
        if self.target:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == 'tool-tip' and self.target:
            match = re.match(r'(No|[\d,]+) contributions?\b', ''.join(self.parts))
            if match:
                self.counts[self.target] = 0 if match[1] == 'No' else int(match[1].replace(',', ''))
            self.target = None

    def days(self):
        if len(self.cells) < 350 or set(self.cells) - self.counts.keys():
            raise ValueError('Incomplete GitHub calendar; previous data preserved')
        result = sorted(({'date': d, 'count': self.counts[k]} for k, d in self.cells.items()), key=lambda x: x['date'])
        validate(result)
        return result

def validate(days):
    if not days:
        raise ValueError('Empty calendar')
    previous = None
    for day in days:
        current = date.fromisoformat(day['date'])
        if type(day['count']) is not int or day['count'] < 0:
            raise ValueError('Invalid count')
        if previous and current != previous + timedelta(days=1):
            raise ValueError('Duplicate, unsorted or missing date')
        previous = current

def stats(days):
    validate(days)
    months = defaultdict(int)
    best = run = 0
    for day in days:
        months[day['date'][:7]] += day['count']
        run = run + 1 if day['count'] else 0
        best = max(best, run)
    return months, best, sum(d['count'] > 0 for d in days), max(days, key=lambda d: d['count'])

def text(x, y, value, size=16, fill=INK, cls='', extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" class="{cls}" {extra}>{escape(str(value))}</text>'

def font_css():
    return ''.join(f"@font-face{{font-family:{name};src:url(data:font/woff;base64,{base64.b64encode((ROOT/'fonts'/file).read_bytes()).decode()}) format('woff')}}" for name, file in [('Serif','serif.woff'),('Sans','sans.woff')])

def card(name, title, h, body, width=1000, bg=PAPER):
    reduced = os.getenv('STATIC') == '1'
    stop = '*{animation:none!important;opacity:1!important;transform:none!important}.smil{display:none!important}'
    css = font_css() + '''text{font-family:Sans,Arial,sans-serif}.serif{font-family:Serif,Georgia,serif}.label{letter-spacing:2px}.in{animation:rise .9s both;animation-delay:var(--d,0s)}.bar{transform-box:fill-box;transform-origin:center bottom;animation:grow 1s both;animation-delay:var(--d,0s)}.cell{animation:appear .5s both;animation-delay:var(--d,0s)}.orbit{transform-origin:830px 160px;animation:rotate 24s linear infinite}.pulse{animation:pulse 3s ease-in-out infinite}@keyframes rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}@keyframes appear{from{opacity:0}to{opacity:1}}@keyframes rotate{to{transform:rotate(360deg)}}@keyframes pulse{50%{opacity:.35}}'''
    css += stop if reduced else '@media(prefers-reduced-motion:reduce){'+stop+'}'
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{h}" viewBox="0 0 {width} {h}" role="img" aria-labelledby="title"><title id="title">{escape(title)}</title><style>{css}</style><rect width="{width}" height="{h}" rx="16" fill="{bg}"/>{body}</svg>'
    (ROOT/'cards'/f'{name}.svg').write_text(svg, encoding='utf-8')

def render(days):
    (ROOT/'cards').mkdir(exist_ok=True)
    months, streak, active, busiest = stats(days)
    total = sum(d['count'] for d in days)
    portrait = json.loads((ROOT/'data'/'portrait.json').read_text())
    body = text(42,42,'GABRIEL GARABEDIAN  /  DESENVOLVIMENTO DE SOFTWARE',12,cls='label')
    body += '<path d="M42 62H958" stroke="#d9d9cf"/>'
    body += '<g class="in">'+text(40,137,'Gabriel',80,cls='serif')+text(40,210,'Garabedian.',80,BLUE,'serif')+'</g>'
    if os.getenv('STATIC') != '1':
        body += '<defs><linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="-300" x2="0"><stop stop-color="#244ce4"/><stop offset=".5" stop-color="#8ba6ff"/><stop offset="1" stop-color="#244ce4"/><animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="1200 0" dur="6s" repeatCount="indefinite"/></linearGradient></defs>'
        body += text(40,210,'Garabedian.',80,'url(#shine)','serif smil in')
    body += text(43,259,'Estudante de ADS · Back-end & desenvolvimento web',19)
    body += text(43,293,'Java / Spring Boot / SQL / Python / JavaScript',14,'#66685d')
    body += '<circle cx="48" cy="339" r="4" fill="#244ce4" class="pulse"/>'+text(61,344,'RECIFE, BRASIL',11,cls='label')+text(400,344,'CONSTRUIR. ENTENDER. EVOLUIR.',11,cls='label')
    body += '<circle cx="830" cy="180" r="115" fill="#eeede5"/>'
    for i,line in enumerate(portrait):
        body += text(740,104+i*4.4,line,4.4,BLUE,'in',f'style="font-family:monospace;white-space:pre;--d:{i*.018}s" xml:space="preserve"')
    body += '<g class="orbit"><circle cx="830" cy="160" r="128" fill="none" stroke="#c4c8d7" stroke-dasharray="3 9"/><circle cx="958" cy="160" r="5" fill="#e3b92e"/></g>'
    card('hero','Gabriel Garabedian — estudante de ADS e desenvolvimento de software',378,body)
    body = text(40,42,'01 / CONSTÂNCIA',11,cls='label')+text(40,86,'Um pouco, todos os dias.',38,cls='serif')+text(958,80,f'{total:,} contribuições'.replace(',','.'),18,BLUE,extra='text-anchor="end"')
    start = date.fromisoformat(days[0]['date'])
    offset = (start.weekday()+1)%7
    palette = ['#e5e6dd','#c5cef9','#93a7f5','#5478ed',BLUE]
    maximum=max(d['count'] for d in days) or 1
    for i,d in enumerate(days):
        col,row=divmod(i+offset,7)
        level = 0 if not d['count'] else min(4,1+int(3*d['count']/maximum))
        body += f'<rect x="{42+col*17}" y="{113+row*17}" width="13" height="13" rx="3" fill="{palette[level]}" class="cell" style="--d:{.3+col*.018}s"><title>{d["date"]}: {d["count"]}</title></rect>'
    body += text(42,262,f'{days[0]["date"]} — {days[-1]["date"]} · calendário público do GitHub',11,'#66685d')
    card('contributions',f'{total} contribuições no calendário público',285,body)
    body=text(40,40,'02 / ATIVIDADE',11,cls='label')+text(40,85,'O trabalho, mês a mês.',38,cls='serif')
    body+=text(40,137,str(streak),34,BLUE,'serif')+text(40,160,'dias · maior sequência',12)
    body+=text(40,204,str(active),34,BLUE,'serif')+text(40,227,'dias com contribuições',12)
    body+=text(40,269,str(busiest['count']),34,BLUE,'serif')+text(40,292,f'melhor dia · {busiest["date"]}',12)
    monthnames=['JAN','FEV','MAR','ABR','MAI','JUN','JUL','AGO','SET','OUT','NOV','DEZ']
    maxmonth=max(months.values()) or 1
    for i,(month,count) in enumerate(months.items()):
        x=300+i*50
        height=150*count/maxmonth
        body+=f'<rect x="{x}" y="{262-height}" width="30" height="{height}" rx="4" fill="{BLUE if count==maxmonth else "#c8cddd"}" class="bar" style="--d:{.4+i*.06}s"/>'
        body+=text(x+15,252-height,count,11,extra='text-anchor="middle"')+text(x+15,283,monthnames[int(month[-2:])-1],9,extra='text-anchor="middle"')+text(x+15,298,month[:4],8,'#66685d',extra='text-anchor="middle"')
    card('activity','Contribuições mensais e maior sequência no período exibido',326,body)
    for i,(name,label,headline,lines,color) in enumerate([
        ('build','DESENVOLVIMENTO','Construir.',['Java, Spring Boot e SQL.','Da lógica à aplicação.'],BLUE),
        ('projects','PROJETOS','Resolver.',['Produtos em prática.','Problemas reais, código real.'],'#c94732'),
        ('learn','APRENDIZADO','Evoluir.',['ADS e estudos em DevOps.','Aprendizado contínuo.'],'#e3b92e')]):
        fg=INK if i==2 else '#fffdf6'
        body=f'<g class="in" style="--d:{.7+i*.15}s">'+text(25,35,f'0{i+1} / {label}',9,fg,'label')+text(25,112,headline,48,fg,'serif')+text(25,151,lines[0],12,fg)+text(25,173,lines[1],12,fg)+text(277,216,'↗',27,fg)+'</g>'
        body+='<circle cx="301" cy="9" r="60" fill="none" stroke="'+fg+'" opacity=".18"/>'
        card(name,headline+' '+' '.join(lines),238,body,324,color)
    for i,(slug,title,desc,stack) in enumerate([
        ('damassa','Da Massa','Cardápio digital: uma experiência web para escolher e pedir.','PYTHON / FLASK / POSTGRESQL'),
        ('neuroin','NeuroIn','Aplicação web com interface própria e notificações Web Push.','WEB / INTERFACE / NOTIFICAÇÕES')]):
        body=text(40,36,f'0{i+3} / PROJETO EM DESTAQUE',10,cls='label')+text(40,87,title,42,cls='serif')+text(40,121,desc,16,'#66685d')+text(40,165,stack,10,BLUE,'label')+text(930,92,'↗',42,BLUE)
        card(slug,title+' — '+desc,193,body)
    card('footer','Aberto a conexões e troca de conhecimento',85,text(40,49,'Vamos construir a próxima ideia.',29,cls='serif')+text(958,47,'GITHUB  /  LINKEDIN ↗',11,BLUE,'label',extra='text-anchor="end"'))

def main():
    path=ROOT/'data'/'contributions.json'
    if '--refresh' in sys.argv:
        # shortcut: public HTML parser, migrate to GraphQL if GitHub changes calendar markup.
        request=Request('https://github.com/users/Gabriel-Garabedian/contributions',headers={'User-Agent':'profile-cards','Accept-Language':'en-US'})
        with urlopen(request,timeout=30) as response:
            html=response.read().decode('utf-8')
        parser=Calendar(); parser.feed(html)
        days=parser.days()
        temporary=path.with_suffix('.tmp')
        temporary.write_text(json.dumps(days,indent=2)+'\n',encoding='utf-8')
        temporary.replace(path)
    render(json.loads(path.read_text(encoding='utf-8')))

if __name__=='__main__':
    main()

