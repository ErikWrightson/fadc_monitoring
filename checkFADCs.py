import sys
import os
import pandas as pd
import numpy as np

import ROOT


# Main execution
if __name__ == "__main__":

    #if(sys.argc == 2):
        #print("Please input only the root file to print.")
    file_path = sys.argv[1]

    pdfName = file_path
    pdfName = pdfName.split('/')[-1]
    pdfName = pdfName.replace(".root", "")
    pdfName = pdfName +"_FADC_Distribution.pdf"
    
    title = "FADC Boards with Cluster Centers from VTP Run: " + pdfName[5:11] + " evio: " + pdfName[18:21] + ";Slot;FADC crate"

    # Open the ROOT file in read mode
    root_file = ROOT.TFile.Open(file_path, "READ")
    if not root_file or root_file.IsZombie():
        print(f"Error: Could not open file {file_path}")
        exit(1)

    
    tree = root_file.Get("recon")

    entries = tree.GetEntries()


    FADC_hist = ROOT.TH2F("FADC_hist", title, 18, 2.5, 20.5, 7, 0.5, 7.5)
    name = ""
    df = pd.read_csv('hycal_daq_connections.txt', sep=r'\s+')
    df = df.set_index('name')
    for i in range(0, entries):
        tree.GetEntry(i)
        if(i % 10000 == 0 or i > entries-10000):
            print(f"\rProcessing item {i}/{entries}", end="", flush=True)
        vtp_clCenters = tree.vtp_cl_center
        
        if tree.trigger_bits & (1<<11):

            for cl in vtp_clCenters:
                if(cl > 1000):
                    name = "W" + str(cl-1000)
                else:
                    name = "G" + str(cl)
                    print("G")
            
                #result = df.loc[df['name'] == name,['name','crate','slot']]

                #FADC_hist.Fill(result['slot'].item(), result['crate'].item()+1)
                FADC_hist.Fill(df.at[name, 'slot'], df.at[name,'crate']+1)

         
    c = ROOT.TCanvas("c1", "FADC Canvas", 1000, 1000)
    c.cd(1)
    FADC_hist.GetXaxis().SetRangeUser(2.5, 20.5)
    FADC_hist.SetStats(0)
    FADC_hist.Draw("COLZ")
    #ROOT.gPad.SetGrid()

    # Keep references to boxes so they aren't garbage collected
    boxes = []

    for ix in range(1, FADC_hist.GetNbinsX() + 1):
        x1 = FADC_hist.GetXaxis().GetBinLowEdge(ix)
        x2 = FADC_hist.GetXaxis().GetBinUpEdge(ix)

        for iy in range(1, FADC_hist.GetNbinsY() + 1):
            y1 = FADC_hist.GetYaxis().GetBinLowEdge(iy)
            y2 = FADC_hist.GetYaxis().GetBinUpEdge(iy)

            box = ROOT.TBox(x1, y1, x2, y2)
            box.SetFillStyle(0)      # Transparent fill
            box.SetLineColor(ROOT.kBlack)
            box.SetLineWidth(1)
            box.Draw("same")

            boxes.append(box)  # Prevent Python from deleting the object

    ROOT.gPad.Update()
    
    c.Print(pdfName)
    c.Clear()


    FADC_hist.Delete()
    # Close the file safely
    root_file.Close()
    print(pdfName)