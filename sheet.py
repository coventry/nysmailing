from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.rl_config import defaultPageSize
from reportlab.lib import utils
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER

style = ParagraphStyle(name='normal', fontSize=12, leading=14.4)
heading = ParagraphStyle(name='heading', fontSize=18, leading=21.6,
                         alignment=TA_CENTER)
center = ParagraphStyle(name='', alignment=TA_CENTER, fontSize=12, leading=14.4)

margin = 0.125*inch

# Dimensions for a quarter page, so that it fits on a single page
qheight = 0.96125*(8.5*inch-2*margin)/2
qwidth = (11*inch-2*margin)/2

class RotatedImage(Image):

    def wrap(self,availWidth,availHeight):
        h, w = Image.wrap(self,availHeight,availWidth)
        print h, w, availHeight, availWidth
        return w, h
    def draw(self, ):
        self.canv.rotate(90)
        self.canv.translate(-50,-810)
        Image.draw(self)

# Made with convert -density 300 voteform.pdf voteform.png
formpath = 'voteform-0.png'
# 612 x 1008
iw, ih = utils.ImageReader(formpath).getSize()
aspect = ih / float(iw)
height = 800
voteform = RotatedImage(formpath, height=height, width=height/aspect)

def address(addr):
    if 'freeaddr' in addr:
        return '<br/>\n'.join(
            ['%s %s' % (addr['fname'], addr['lname'])] + 
            filter(None, [l.strip() for l in addr['freeaddr']]))
    return '''
    {fname} {lname}<br/>
    {street}<br/>
    {city} {state} {zip}'''.format(**addr)

fromaddrstyle = style
toaddrstyle = ParagraphStyle(name='toaddrstyle',  leftIndent=0.5*inch,
                             fontSize=15, leading=18)
    
postagebox = ParagraphStyle(
    name='postagebox', borderColor=colors.black, borderWidth=3, borderPadding=5,
    fontSize=12)
postage =[Spacer(1,0.2*inch), Paragraph('<b>Postage</b>', postagebox)]

def fromaddr(addr):
    return Paragraph(address(addr), fromaddrstyle)
def toaddr(addr):
    return Paragraph('<b>%s</b>' % address(addr), toaddrstyle)
def disclaimer(fromaddr, toaddr):
    return Table([[
        [Paragraph("""

        <b>%s %s, REGISTER AS A DEMOCRAT BY OCT  9 OR LOSE YOUR SAY OVER WHO'S
        IN THE WHITE HOUSE!</b>

        """ % (toaddr['fname'].upper(), toaddr['lname'].upper()), style)],
        Spacer(1,0.5*inch)],
        [Paragraph("""

        {fname} {lname}  (address above)  used nysmailing.com  and his
        personal resources to prepare & send this form, without anyone
        else's permission, because <b>he wants YOUR vote to COUNT!</b>

        """.format(**fromaddr), postagebox, )
        ]], colWidths=[0.95*qwidth], # rowHeights=[0.5*inch, 1*inch],
            style=[('ALIGN', (0,0), (-1,-1), 'CENTER'),
                   ('VALIGN',(0,0), (-1,-1), 'TOP')])


def instructions(addr, _):
    return Table([[[
        Spacer(1,0.25*inch),
        Paragraph("""

    {fname} {lname},  when you've completed the  form overleaf, please
    refold the sheet so this  quadrant is exposed.  To avoid confusion
    about the destination address,  please fold vertically first, then
    horizontally. Then please tape back  it up, stamp it if necessary,
    and mail it back.

    """.format(**addr), postagebox)]]])
        

def envelope(fromaddr_, toaddr_, disclaimer):
    return [Spacer(1, inch/16),
            Table([[fromaddr(fromaddr_), postage]],
                 colWidths=[qwidth*0.75, 0.85*inch], # rowHeights=[0.2*qheight],
                  style = [# ('GRID', (0,0), (-1,-1), 1, colors.black),
                           ('VALIGN', (0,0), (0,0), 'TOP'),
                           ('VALIGN', (1,0), (1,0), 'CENTER'),
                           ],
                  ),
            Spacer(1, 0.5*inch), 
            toaddr(toaddr_),
            Spacer(1, 0.25*inch),
            disclaimer(fromaddr_, toaddr_),
            ]

def c2a(addr):
    return [
        Paragraph("""

        <b>{fname} {lname}!</b><br/>
        DON'T LOSE YOUR SAY OVER<br/>
        WHO'S IN THE WHITE HOUSE!<br/>
        <B>USE THIS FORM BY OCT 9</B>
        """.format(**addr), heading),
        Spacer(1, 0.1*inch),
        Paragraph("""

        NYS voter  rolls as of August  22 suggest that you  are <b>not
  registered</b> to vote in  the 2016 Democratic Presidential Primary.
  If  that's the  case,  to  have any  influence  over  who your  next
  President will be  you <b>must, before Oct 9</b>,  complete and mail
  in the form  overleaf and check "Democratic Party"  for question 14.
  Current polls suggest that  the Democratic Presidential nominee will
  likely  be the  next US  President.  <B>Therefore,  the presidential
  election which matters  in 2016 is the Democratic  Primary.  You are
  not  obliged to  identify with  the  Democratic Party  to take  this
  ELECTORAL REALITY into account.</b>

  """, style),
        Spacer(1, 0.1*inch),
        Paragraph("""
        To send  the form in  you can simply refold  this sheet so  that the
Board of  Elections quadrant is  exposed, affix a stamp  if necessary,
tape it back up, and stick it back in the mail.  """, style),]

def bernie(addr):
    normal = ParagraphStyle(name='normal', fontSize=12)
    center = ParagraphStyle(name='center', alignment=TA_CENTER, fontSize=12)
    check = Paragraph('<b>Yes</b>', center)
    return [
        Paragraph('''

        {fname} {lname}, unless thousands of  people like you use this
        form, New York and the USA is likely to go for Hillary Clinton
        in 2016.  For a better alternative, please see feelthebern.org
        or berniesanders.com

        '''.format(**addr),style),
        Spacer(1, 0.225*inch),
        Paragraph('''<b>Bernie 2016:</b>''', heading),
        Paragraph('''

        Why settle for the lesser of  two evils, <br/>
        <b>when you can have the greater good?</b>

        ''', center),
        Spacer(0, 0.225*inch),
        Table([
        [Paragraph('<b>Issue</b>', normal), Paragraph('<b>Bernie</b>', center), Paragraph('Hillary', center)],
        ["End Citizen's United (i.e., end big money in politics)", check, '??'],
        ['Minimum wage of $15/hour', check, '$12'],
        ['Free Public College for all', check, 'No'],
        ['Free medicare for all', check, 'No'],
        ['Decriminalize marijuana & legalize medical', check, '??'],
        ['Break up the big banks', check, 'No'],
        ['Tax on large Wall Street transactions', check, '??'],
        ['End tax breaks on huge incomes (over $500K/yr)', check, '??'],
        ['Racial & Gender equity and fairness', check, check],
        ],
              rowHeights=10*[0.22*inch],
              style=[('ALIGN', (1,0), (-1,-1), 'CENTER'),
                     ('LINEABOVE', (0,1), (-1,1), 2, colors.black),
                     ('LINEBEFORE', (2,0), (2,-1), 2, colors.black)]
        )
        ]

def addrsheet(fromaddr, toaddr, boeaddr):
    return [Spacer(1,0.095*inch),
            Table([
        [envelope(fromaddr, toaddr,  disclaimer), envelope(toaddr,   boeaddr, instructions) ],
        [c2a(toaddr), bernie(toaddr)],
                  ],
                  colWidths=[qwidth, qwidth], rowHeights=[qheight, qheight],
                  style=[# ('GRID', (0,0), (-1,-1), 1, colors.black),
                         ('LINEABOVE', (0,1), (-1,-1), 0.5, colors.black),
                         ('LINEBEFORE', (1, 0), (-1,-1), 0.5, colors.black),
                         ('VALIGN', (0,0), (-1,-1), 'TOP')]),
            PageBreak(),
            voteform
            ]

def makedoc(filename):
    return SimpleDocTemplate(filename,
                             leftMargin=margin, rightMargin=margin,
                             topMargin=margin, bottomMargin=margin,
                             pagesize=landscape(letter),
                             showBoundary=False)

# Test data & routine
myaddr = dict(fname='Alex', lname='Coventry', street='135 Lawnview Ave',
              city='North Hampton', state='OH', zip='45349')
hollyaddr = dict(fname='Holly', lname='White', street='267 Genesee Park Dr',
                 city='Syracuse', state='NY', zip='13224')
boeaddr = dict(fname='Tompkins County Board of Elections', lname='', street='128 E. BUFFALO ST',
                 city='Ithaca', state='NY', zip='14850')

def go():
     doc = makedoc('phello.pdf')
     doc.build(addrsheet(myaddr, hollyaddr, boeaddr))
     return doc

if __name__ == '__main__':
    go()
