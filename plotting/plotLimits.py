from ROOT import TCanvas, TGraph, TGraphAsymmErrors, TLegend, TLatex
from array import array
from sys import argv,stdout
from tdrStyle import *
setTDRStyle()

VERBOSE=False

resonantXsecs = {
  1100 : 3.91,
  900 : 9.37,
  1300 : 1.81,
  1500 : 0.9,
  1700 : 0.47,
  1900 : 0.25,
  2100 : 0.14,
    }

fcncXsecs = {
  300 : 27.6,
  500 : 6.52,
  700 : 2.06,
  900 : 0.78,
  1100 : 0.33,
  1300 : 0.15,
  1500 : 0.076
    }


def parseLine(l):
  if 'Observed' in l:
    return 'Observed',float(l.split('<')[1])
  return float(l.split()[1].strip(':%')),float(l.split('<')[1])

def makePlot(finname,foutname,plottitle='',masstitle='',scale=False):
  xsecs = resonantXsecs if 'resonant' in finname else fcncXsecs
  points = {}
  cls = [2.5, 16, 50, 84, 97.5,'Observed']
  xaxis = []
  for cl in cls:
    points[cl] = []
  xsec=1
  for l in open(finname):
    try:
      if l.strip()[0]=='#':
        continue
      if 'MASS' in l:
        if scale:
          xsec = xsecs[int(l.split()[1])] 
        if VERBOSE:
          print ''
          stdout.write('$%6s$ & $%7.3g$'%(l.split()[1],xsec/(0.667)))
        xaxis.append(float(l.split()[1]))
      else:
        cl,val = parseLine(l)
        points[cl].append(val/xsec)
        if VERBOSE and (cl==50 or cl=='Observed'):
          stdout.write(' & $%10.4g$'%(val/xsec))
    except:
      pass
  if VERBOSE:
    print ''
  
  N = len(xaxis)
  up1Sigma=[]; up2Sigma=[]
  down1Sigma=[]; down2Sigma=[]
  for iM in xrange(N):
    up1Sigma.append(points[84][iM]-points[50][iM])
    up2Sigma.append(points[97.5][iM]-points[50][iM])
    down1Sigma.append(-points[16][iM]+points[50][iM])
    down2Sigma.append(-points[2.5][iM]+points[50][iM])
  
  up1Sigma = array('f',up1Sigma)
  up2Sigma = array('f',up2Sigma)
  down1Sigma = array('f',down1Sigma)
  down2Sigma = array('f',down2Sigma)
  cent = array('f',points[50])
  obs = array('f',points['Observed'])
  xarray = array('f',xaxis)

  xsecarray = array('f',[xsecs[xx] for xx in xaxis])
  xsecarrayLow = array('f',[0.0625*xsecs[xx] for xx in xaxis])
  onearray = array('f',[1 for xx in xaxis])
  graphXsec = TGraph(N,xarray,xsecarray)
  graphXsecLow = TGraph(N,xarray,xsecarrayLow)
  graphOne = TGraph(N,xarray,onearray)

  zeros = array('f',[0 for i in xrange(N)])
  graphCent = TGraph(N,xarray,cent)
  graphObs = TGraph(N,xarray,obs)
  graph1Sigma = TGraphAsymmErrors(N,xarray,cent,zeros,zeros,down1Sigma,up1Sigma)
  graph2Sigma = TGraphAsymmErrors(N,xarray,cent,zeros,zeros,down2Sigma,up2Sigma)
  c = TCanvas('c','c',700,600)
  c.SetLogy()
  c.SetLeftMargin(.15)
  graph2Sigma.GetXaxis().SetTitle(masstitle+' [GeV]')
  if scale:
    graph2Sigma.GetYaxis().SetTitle('Upper limit [#sigma/#sigma_{theory}]')  
  else:
    graph2Sigma.GetYaxis().SetTitle("Upper limit [#sigma] [pb]")  
  graph2Sigma.SetLineColor(5)
  graph1Sigma.SetLineColor(3)
  graph2Sigma.SetFillColor(5)
  graph1Sigma.SetFillColor(3)
  graph2Sigma.SetMinimum(0.5*min(points[2.5]))
  if scale:
    graph2Sigma.SetMaximum(10*max(max(points[97.5]),max(xsecarray),4))
  else:
    graph2Sigma.SetMaximum(10*max(max(points[97.5]),max(xsecarray)))
  graphCent.SetLineWidth(2)
  graphCent.SetLineStyle(2)
  graphObs.SetLineColor(1)
  graphObs.SetLineWidth(3)
  graph1Sigma.SetLineStyle(0)
  graph2Sigma.SetLineStyle(0)
 
  leg = TLegend(0.55,0.7,0.9,0.9)
  leg.AddEntry(graphCent,'Expected','L')
  leg.AddEntry(graphObs,'Observed','L')
  leg.AddEntry(graph1Sigma,'1 #sigma','F')
  leg.AddEntry(graph2Sigma,'2 #sigma','F')
  leg.SetFillStyle(0)
  leg.SetBorderSize(0)

  graph2Sigma.Draw('A3')
  graph1Sigma.Draw('3 same')
  graphCent.Draw('same L')
  graphObs.Draw('same L')
  if scale:
    graphOne.SetLineColor(2)
    graphOne.SetLineWidth(2)
    graphOne.SetLineStyle(2)
    graphOne.Draw('same L')
  else:
    graphXsec.SetLineColor(2)
    graphXsecLow.SetLineColor(4)
    subscript = 'SR' if 'Resonant' in plottitle else 'FC'
    leg.AddEntry(graphXsec,'theory a_{%s}=b_{%s}=0.1'%(subscript,subscript),'l')
#    leg.AddEntry(graphXsecLow,'theory a_{%s}=b_{%s}=0.025'%(subscript,subscript),'l')
    for g in [graphXsec]:
      g.SetLineWidth(2)
      g.SetLineStyle(2)
      g.Draw('same L')
  leg.Draw()
  label = TLatex()
  label.SetNDC()
  label.SetTextFont(62)
  label.SetTextAlign(11)
  label.DrawLatex(0.19,0.85,"CMS")
  label.SetTextFont(52)
  label.DrawLatex(0.28,0.85,"Preliminary")
  label.SetTextFont(42)
  label.SetTextSize(0.6*c.GetTopMargin())
  label.DrawLatex(0.19,0.77,plottitle)
  if scale:
    if 'Resonant' in plottitle:
      label.DrawLatex(0.19,0.7,"a_{SR} = b_{SR} = 0.1")
    else:
      label.DrawLatex(0.19,0.7,"a_{FC} = b_{FC} = 0.1")
  label.SetTextSize(0.5*c.GetTopMargin())
  label.SetTextFont(42)
  label.SetTextAlign(31) # align right
  label.DrawLatex(0.9, 0.94,"2.32 fb^{-1} (13 TeV)")
  c.SaveAs(foutname+'.pdf')
  c.SaveAs(foutname+'.png')

makePlot('../datacards/fcnc_obs_limits.txt','~/public_html/figs/monotop/fits_final/fcnc_obs_limits_xsec','#splitline{Flavor-changing}{neutral current}','M_{V}')
makePlot('../datacards/resonant_obs_limits.txt','~/public_html/figs/monotop/fits_final/resonant_obs_limits_xsec','#splitline{Resonant}{production}','M_{S}')
makePlot('../datacards/fcnc_obs_limits.txt','~/public_html/figs/monotop/fits_final/fcnc_obs_limits','#splitline{Flavor-changing}{neutral current}','M_{V}',True)
#makePlot('../datacards/fcnc_obs_limits.txt','~/public_html/figs/monotop/fits_final/fcnc_obs_limits','#splitline{Flavor-changing}{neutral current}','M_{V}',True)
makePlot('../datacards/resonant_obs_limits.txt','~/public_html/figs/monotop/fits_final/resonant_obs_limits','#splitline{Resonant}{production}','M_{S}',True)