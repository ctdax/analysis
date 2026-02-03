#!/usr/bin/env python3
"""
Script to create ratio plots of histograms from ROOT files using pyROOT.
Specifically designed for HSCP analysis with configurable parameters.
"""

import ROOT
import os
import sys
import argparse
from pathlib import Path

class HistogramRatioPlotter:
    """Class to handle histogram ratio plotting with configurable parameters."""
    
    def __init__(self, base_dir="/eos/user/c/cthompso/analysis/CMSSW_15_0_16/src"):
        self.base_dir = Path(base_dir)
        self.ntuples_dir = self.base_dir / "ntuples"
        self.plots_dir = self.base_dir / "plots"
        
        # Ensure plots directory exists
        self.plots_dir.mkdir(exist_ok=True)
        
        # ROOT setup
        ROOT.gROOT.SetBatch(True)  # Run in batch mode
        ROOT.gStyle.SetOptStat(0)  # Disable stat box
        
        # Define custom colors
        self.custom_colors = [
            "#3f90da", "#ffa90e", "#bd1f01", "#94a4a2", "#832db6",
            "#a96b59", "#e76300", "#b9ac70", "#717581", "#92dadd"
        ]
        
    def format_ctau_label(self, ctau, decay_type):
        """Format ctau label with abbreviations and decay type."""
        # Handle abbreviations
        if ctau == "10000mm":
            ctau_display = "10k"
        elif ctau == "1000mm":
            ctau_display = "1k"
        else:
            ctau_display = ctau.replace('p', '.').replace('mm', '')
        
        # Add decay type indicator
        decay_label = "(L)" if decay_type == "lightDecay" else "(H)"
        
        return fr"c\tau = {ctau_display} mm {decay_label}"
        
    def construct_filename(self, gluino_mass, neutralino_mass, ctau, decay_type, era="130X_mcRun3_2023_realistic_postBPix_v2"):
        """
        Construct the ROOT filename based on parameters.
        
        Args:
            gluino_mass (int): Gluino mass in GeV
            neutralino_mass (int): Neutralino mass in GeV  
            ctau (str): ctau value (e.g., "0p1mm", "10000mm")
            decay_type (str): Decay type ("lightDecay" or "heavyDecay")
            era (str): Data-taking era identifier
            
        Returns:
            str: Constructed filename
        """
        return f"gluino{gluino_mass}_chi10{neutralino_mass}_{ctau}_{decay_type}_{era}.root"
    
    def load_histogram(self, filename, hist_name):
        """
        Load histogram from ROOT file.
        
        Args:
            filename (str): ROOT file name
            hist_name (str): Name of histogram to load
            
        Returns:
            ROOT.TH1: Loaded histogram or None if failed
        """
        filepath = self.ntuples_dir / filename
        
        if not filepath.exists():
            print(f"Error: File {filepath} not found!")
            return None
            
        root_file = ROOT.TFile.Open(str(filepath), "READ")
        if not root_file or root_file.IsZombie():
            print(f"Error: Cannot open file {filepath}")
            return None
            
        # Automatically prepend HSCPMiniAODAnalyzer directory
        full_hist_name = f"HSCPMiniAODAnalyzer/{hist_name}"
        hist = root_file.Get(full_hist_name)
        if not hist:
            full_hist_name = f"HSCPFullAODAnalyzer/{hist_name}"
            hist = root_file.Get(full_hist_name)
            if not hist:
                print(f"Error: Histogram '{full_hist_name}' not found in {filename}")
                root_file.Close()
                return None
            
        # Clone the histogram to keep it in memory after file closure
        hist_clone = hist.Clone(f"{hist_name}_{filename.replace('.root', '')}")
        hist_clone.SetDirectory(0)  # Detach from file

        # Normalize histogram entries so total "AllEvents" = 1
        eventCount = hist_clone.GetBinContent(1) 
        if eventCount > 0:
            hist_clone.Scale(1.0 / eventCount)
        else:
            print(f"Warning: Histogram '{full_hist_name}' in {filename} has zero events, cannot normalize.")

        root_file.Close()
        
        return hist_clone
    
    def create_ratio_plot(self, hist1, hist2, title="Ratio Plot"):
        """
        Create a ratio plot of two histograms.
        
        Args:
            hist1 (ROOT.TH1): Numerator histogram
            hist2 (ROOT.TH1): Denominator histogram
            title (str): Title for the ratio plot
            
        Returns:
            ROOT.TH1: Ratio histogram
        """
        if not hist1 or not hist2:
            print("Error: One or both histograms are None")
            return None
            
        # Create ratio histogram
        ratio = hist1.Clone(f"ratio_{hist1.GetName()}_{hist2.GetName()}")
        ratio.SetTitle(title)
        ratio.Divide(hist2)
        
        # Style the ratio histogram
        ratio.SetLineColor(ROOT.kBlack)
        ratio.SetMarkerStyle(20)
        ratio.SetMarkerSize(0.8)
        ratio.GetYaxis().SetTitle("Ratio")
        ratio.GetYaxis().SetTitleSize(0.05)
        ratio.GetYaxis().SetLabelSize(0.04)
        ratio.GetXaxis().SetTitleSize(0.05)
        ratio.GetXaxis().SetLabelSize(0.04)
        
        return ratio
    
    def save_ratio_plot(self, hist1, hist2, ratio_hist, output_name, numerator_label="Numerator", denominator_label="Denominator", log_scale=False, y_range=None):
        """
        Save the comparison and ratio plot as PDF.
        
        Args:
            hist1 (ROOT.TH1): First histogram (numerator)
            hist2 (ROOT.TH1): Second histogram (denominator)
            ratio_hist (ROOT.TH1): Ratio histogram to save
            output_name (str): Output filename (without extension)
            numerator_label (str): Label for numerator in legend
            denominator_label (str): Label for denominator in legend
            log_scale (bool): Use logarithmic scale for y-axis of top plot
            y_range (list[float] or None): List of y-axis tick positions for the ratio pad. If None, default ROOT range are used.
        """
        if not hist1 or not hist2 or not ratio_hist:
            print("Error: One or more histograms are None")
            return
            
        # Create canvas with two pads
        canvas = ROOT.TCanvas("canvas", "Comparison and Ratio Plot", 800, 800)
        
        # Create pads: top for comparison, bottom for ratio
        pad1 = ROOT.TPad("pad1", "Histogram comparison", 0, 0.3, 1, 1)
        pad2 = ROOT.TPad("pad2", "Ratio", 0, 0, 1, 0.3)
        
        pad1.SetBottomMargin(0.1)  # Increased bottom margin to show x-axis labels
        pad2.SetTopMargin(0.02)
        pad2.SetBottomMargin(0.4)
        
        # Set log scale if requested
        if log_scale:
            pad1.SetLogy()
        
        pad1.Draw()
        pad2.Draw()
        
        # Top pad: draw histograms
        pad1.cd()
        
        # Style histograms
        hist1_copy = hist1.Clone("hist1_styled")
        hist2_copy = hist2.Clone("hist2_styled")
        
        # Set custom colors
        color1 = ROOT.TColor.GetColor(self.custom_colors[0])
        color2 = ROOT.TColor.GetColor(self.custom_colors[1])
        
        hist1_copy.SetLineColor(color1)
        hist1_copy.SetLineWidth(2)
        hist2_copy.SetLineColor(color2)
        hist2_copy.SetLineWidth(2)
        
        # Improve x-axis labels visibility
        hist1_copy.GetXaxis().SetLabelSize(0.045)
        hist1_copy.GetXaxis().SetTitleSize(0.045)

        # Draw custom y-axis range if requested
        if y_range:
            hist1_copy.GetYaxis().SetRangeUser(min(y_range), max(y_range))
            hist2_copy.GetYaxis().SetRangeUser(min(y_range), max(y_range))
        
        # Draw histograms
        hist1_copy.Draw("HIST")
        hist2_copy.Draw("HIST SAME")
        
        # Add legend without border
        legend = ROOT.TLegend(0.6, 0.7, 0.85, 0.85)
        legend.SetBorderSize(0)
        legend.AddEntry(hist1_copy, numerator_label, "l")
        legend.AddEntry(hist2_copy, denominator_label, "l")
        legend.Draw()
        
        # Bottom pad: draw ratio
        pad2.cd()
        
        # Style ratio histogram
        ratio_hist.SetLineColor(ROOT.kBlack)
        ratio_hist.SetMarkerStyle(20)
        ratio_hist.SetMarkerSize(0.8)
        ratio_hist.GetYaxis().SetTitle("Ratio")
        ratio_hist.GetYaxis().SetTitleSize(0.12)
        ratio_hist.GetYaxis().SetLabelSize(0.1)
        ratio_hist.GetYaxis().SetTitleOffset(0.35)  # Bring y-axis title closer to plot
        ratio_hist.GetXaxis().SetTitleSize(0.12)
        ratio_hist.GetXaxis().SetLabelSize(0.1)
        ratio_hist.SetTitle("")  # Remove title
        ratio_hist.Draw("EP")  # Draw with error bars

        # Add horizontal line at y=1
        line = ROOT.TLine(ratio_hist.GetXaxis().GetXmin(), 1.0, 
                         ratio_hist.GetXaxis().GetXmax(), 1.0)
        line.SetLineColor(ROOT.kRed)
        line.SetLineStyle(2)
        line.Draw("same")
        
        # Go back to main canvas
        canvas.cd()
        
        # Save as PDF
        output_path = self.plots_dir / f"{output_name}.pdf"
        canvas.SaveAs(str(output_path))
        print(f"Comparison and ratio plot saved as: {output_path}")
        
        # Cleanup
        canvas.Close()

def main():
    """Main function to run the ratio plotting script."""
    parser = argparse.ArgumentParser(description="Create ratio plots of histograms from HSCP ROOT files")
    
    # Configuration parameters
    parser.add_argument("--hist-name", default="EventCutFlow", 
                       help="Name of histogram to create ratio of (default: EventCutFlow)")
    parser.add_argument("--gluino-mass", type=int, default=1800,
                       help="Gluino mass in GeV (default: 1800)")
    parser.add_argument("--neutralino-mass", type=int, default=1300,
                       help="Neutralino mass in GeV (default: 1300)")
    parser.add_argument("--ctau1", default="0p1mm",
                       help="First ctau value for numerator (default: 0p1mm)")
    parser.add_argument("--ctau2", default="10000mm", 
                       help="Second ctau value for denominator (default: 10000mm)")
    parser.add_argument("--decay-type", default="lightDecay",
                       choices=["lightDecay", "heavyDecay"],
                       help="Decay type (default: lightDecay)")
    parser.add_argument("--era", default="130X_mcRun3_2023_realistic_postBPix_v2",
                       help="Data-taking era (default: 130X_mcRun3_2023_realistic_postBPix_v2)")
    parser.add_argument("--output-name", default="",
                       help="Custom output filename (without extension). If not provided, auto-generated.")
    parser.add_argument("--log-scale", action="store_true",
                       help="Use logarithmic scale for y-axis of top histogram plot")
    parser.add_argument("--y-range", default="1,0.1,0.01,0.001,0.0001",
                       help="Comma-separated list of y-axis tick positions for the ratio pad (default: 1,0.1,0.01,0.001,0.0001)")
    
    args = parser.parse_args()

    # Parse y-range into a list of floats
    try:
        y_range = [float(x) for x in args.y_range.split(",")] if args.y_range else None
    except ValueError:
        print("Error: --y-range must be a comma-separated list of numbers (e.g. 1,0.1,0.01)")
        sys.exit(1)
    
    # Create plotter instance
    plotter = HistogramRatioPlotter()
    
    # Construct filenames
    filename1 = plotter.construct_filename(args.gluino_mass, args.neutralino_mass, 
                                         args.ctau1, args.decay_type, args.era)
    filename2 = plotter.construct_filename(args.gluino_mass, args.neutralino_mass,
                                         args.ctau2, args.decay_type, args.era)
    
    print(f"Loading histograms:")
    print(f"  Numerator: {filename1} -> {args.hist_name}")
    print(f"  Denominator: {filename2} -> {args.hist_name}")
    
    # Load histograms
    hist1 = plotter.load_histogram(filename1, args.hist_name)
    hist2 = plotter.load_histogram(filename2, args.hist_name)
    
    if not hist1 or not hist2:
        print("Error: Failed to load one or both histograms")
        sys.exit(1)
    
    # Create ratio plot
    title = f"{args.hist_name} Ratio: {args.ctau1} / {args.ctau2}"
    ratio_hist = plotter.create_ratio_plot(hist1, hist2, title)
    
    if not ratio_hist:
        print("Error: Failed to create ratio histogram")
        sys.exit(1)
    
    # Generate output filename if not provided
    if args.output_name:
        output_name = args.output_name
    else:
        # Use histogram name directly since it no longer contains directory separators
        output_name = (f"ratio_{args.hist_name}_gluino{args.gluino_mass}_"
                      f"chi10{args.neutralino_mass}_{args.ctau1}_vs_{args.ctau2}_{args.decay_type}")
    
    # Create labels for legend
    numerator_label = plotter.format_ctau_label(args.ctau1, args.decay_type)
    denominator_label = plotter.format_ctau_label(args.ctau2, args.decay_type)
    
    # Save the plot
    plotter.save_ratio_plot(hist1, hist2, ratio_hist, output_name, numerator_label, denominator_label, args.log_scale, y_range=y_range)
    
    print("Ratio plot creation completed successfully!")

if __name__ == "__main__":
    main()
