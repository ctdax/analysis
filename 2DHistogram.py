#!/usr/bin/env python3
"""
Script to create 2D histogram plots from ROOT files using pyROOT.
Specifically designed for HSCP analysis with configurable parameters.
Creates a 2D histogram where each row corresponds to a different ctau value.
"""

import ROOT
import os
import sys
import argparse
import numpy as np
from pathlib import Path

class Histogram2DPlotter:
    """Class to handle 2D histogram plotting with configurable parameters."""
    
    def __init__(self, base_dir="/eos/user/c/cthompso/analysis/CMSSW_15_0_16/src"):
        self.base_dir = Path(base_dir)
        self.ntuples_dir = self.base_dir / "ntuples"
        self.plots_dir = self.base_dir / "plots"
        
        # Ensure plots directory exists
        self.plots_dir.mkdir(exist_ok=True)
        
        # ROOT setup
        ROOT.gROOT.SetBatch(True)  # Run in batch mode
        ROOT.gStyle.SetOptStat(0)  # Disable stat box
        ROOT.gStyle.SetPalette(ROOT.kViridis)  # Use viridis color palette
        
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
            print(f"Error: Histogram '{full_hist_name}' not found in {filename}")
            root_file.Close()
            return None
            
        # Clone the histogram to keep it in memory after file closure
        hist_clone = hist.Clone(f"{hist_name}_{filename.replace('.root', '')}")
        hist_clone.SetDirectory(0)  # Detach from file
        root_file.Close()
        
        return hist_clone
    
    def create_2d_histogram(self, histograms, ctau_labels, hist_name):
        """
        Create a 2D histogram from multiple 1D histograms.
        
        Args:
            histograms (list): List of ROOT.TH1 histograms
            ctau_labels (list): List of ctau labels corresponding to histograms
            hist_name (str): Base name for the histogram
            
        Returns:
            ROOT.TH2F: 2D histogram
        """
        if not histograms or len(histograms) == 0:
            print("Error: No histograms provided")
            return None
            
        # Get dimensions from the first histogram
        first_hist = histograms[0]
        n_x_bins = first_hist.GetNbinsX()
        x_min = first_hist.GetXaxis().GetXmin()
        x_max = first_hist.GetXaxis().GetXmax()
        
        n_ctau = len(histograms)
        
        # Create 2D histogram
        hist_2d = ROOT.TH2F(f"2D_{hist_name}", 
                           f"2D {hist_name}",
                           n_x_bins, x_min, x_max,
                           n_ctau, 0, n_ctau)
        
        # Copy x-axis bin labels from the original histogram if they exist
        for x_bin in range(1, n_x_bins + 1):
            bin_label = first_hist.GetXaxis().GetBinLabel(x_bin)
            if bin_label:  # Only set if label exists
                hist_2d.GetXaxis().SetBinLabel(x_bin, bin_label)
        
        # Set y-axis labels
        for i, label in enumerate(ctau_labels):
            hist_2d.GetYaxis().SetBinLabel(i + 1, label)
        
        # Fill 2D histogram with data from 1D histograms
        for ctau_idx, hist in enumerate(histograms):
            if not hist:
                continue
                
            for x_bin in range(1, n_x_bins + 1):
                bin_content = hist.GetBinContent(x_bin)
                hist_2d.SetBinContent(x_bin, ctau_idx + 1, bin_content)
        
        # Set axis labels
        hist_2d.GetXaxis().SetTitle(first_hist.GetXaxis().GetTitle())
        hist_2d.GetYaxis().SetTitle("ctau [mm] (Decay Type)")
        hist_2d.GetZaxis().SetTitle("Counts")
        
        return hist_2d
    
    def save_2d_plot(self, hist_2d, output_name, log_scale_z=True):
        """
        Save the 2D histogram plot as PDF.
        
        Args:
            hist_2d (ROOT.TH2): 2D histogram to save
            output_name (str): Output filename (without extension)
            log_scale_z (bool): Use logarithmic scale for z-axis (color scale)
        """
        if not hist_2d:
            print("Error: 2D histogram is None")
            return
            
        # Create canvas
        canvas = ROOT.TCanvas("canvas", "2D Histogram Plot", 900, 700)
        canvas.SetRightMargin(0.15)  # Make room for color scale
        
        # Set log scale for z-axis if requested
        if log_scale_z:
            canvas.SetLogz()
        
        # Style the histogram
        hist_2d.SetStats(0)  # Turn off statistics box
        
        # Draw histogram with COLZ option for color scale
        hist_2d.Draw("COLZ")
        
        # Adjust label sizes
        hist_2d.GetXaxis().SetTitleSize(0.045)
        hist_2d.GetXaxis().SetLabelSize(0.04)
        hist_2d.GetYaxis().SetTitleSize(0.045)
        hist_2d.GetYaxis().SetLabelSize(0.04)
        hist_2d.GetYaxis().SetTitleOffset(1.15)  # Proper spacing between title and labels
        hist_2d.GetZaxis().SetTitleSize(0.035)
        hist_2d.GetZaxis().SetLabelSize(0.04)
        
        # Save as PDF
        output_path = self.plots_dir / f"{output_name}.pdf"
        canvas.SaveAs(str(output_path))
        print(f"2D histogram plot saved as: {output_path}")
        
        # Cleanup
        canvas.Close()

def parse_ctau_list(ctau_string):
    """
    Parse comma-separated ctau values from command line argument.
    
    Args:
        ctau_string (str): Comma-separated ctau values
        
    Returns:
        list: List of ctau values
    """
    return [ctau.strip() for ctau in ctau_string.split(',')]

def main():
    """Main function to run the 2D histogram plotting script."""
    parser = argparse.ArgumentParser(description="Create 2D histogram plots from HSCP ROOT files")
    
    # Configuration parameters
    parser.add_argument("--hist-name", default="EventCutFlow", 
                       help="Name of histogram to create 2D plot of (default: EventCutFlow)")
    parser.add_argument("--gluino-mass", type=int, default=1800,
                       help="Gluino mass in GeV (default: 1800)")
    parser.add_argument("--neutralino-mass", type=int, default=1300,
                       help="Neutralino mass in GeV (default: 1300)")
    parser.add_argument("--ctaus", default="0p1mm,1mm,10mm,100mm,1000mm,10000mm",
                       help="Comma-separated list of ctau values (default: 0p1mm,1mm,10mm,100mm,1000mm,10000mm)")
    parser.add_argument("--decay-types", default="lightDecay",
                       help="Decay types: 'lightDecay', 'heavyDecay', or 'both' (default: lightDecay)")
    parser.add_argument("--era", default="130X_mcRun3_2023_realistic_postBPix_v2",
                       help="Data-taking era (default: 130X_mcRun3_2023_realistic_postBPix_v2)")
    parser.add_argument("--output-name", default="",
                       help="Custom output filename (without extension). If not provided, auto-generated.")
    parser.add_argument("--log-scale-z", action="store_true", default=True,
                       help="Use logarithmic scale for z-axis (color scale) (default: True)")
    parser.add_argument("--linear-scale-z", dest="log_scale_z", action="store_false",
                       help="Use linear scale for z-axis (color scale)")
    
    args = parser.parse_args()
    
    # Create plotter instance
    plotter = Histogram2DPlotter()
    
    # Parse ctau list
    ctau_list = parse_ctau_list(args.ctaus)
    
    # Determine which decay types to process
    if args.decay_types.lower() == "both":
        decay_types = ["lightDecay", "heavyDecay"]
    else:
        decay_types = [args.decay_types]
    
    print(f"Creating 2D histogram for:")
    print(f"  Histogram: {args.hist_name}")
    print(f"  Gluino mass: {args.gluino_mass} GeV")
    print(f"  Neutralino mass: {args.neutralino_mass} GeV")
    print(f"  Decay types: {decay_types}")
    print(f"  ctau values: {ctau_list}")
    print(f"  Era: {args.era}")
    
    # Load histograms for all ctau values and decay types
    histograms = []
    valid_labels = []
    
    for decay_type in decay_types:
        for ctau in ctau_list:
            filename = plotter.construct_filename(args.gluino_mass, args.neutralino_mass, 
                                                ctau, decay_type, args.era)
            print(f"  Loading: {filename} -> {args.hist_name}")
            
            hist = plotter.load_histogram(filename, args.hist_name)
            if hist:
                histograms.append(hist)
                # Always create label that includes both ctau and decay type
                decay_label = "L" if decay_type == "lightDecay" else "H"
                
                # Abbreviate ctau values
                if ctau == "1000mm":
                    ctau_display = "1k"
                elif ctau == "10000mm":
                    ctau_display = "10k"
                else:
                    ctau_display = ctau.replace('mm', '').replace('p', '.')
                
                label = f"{ctau_display} ({decay_label})"
                valid_labels.append(label)
            else:
                print(f"  Warning: Skipping {ctau} {decay_type} due to loading failure")
    
    if len(histograms) == 0:
        print("Error: No histograms could be loaded successfully")
        sys.exit(1)
    
    print(f"Successfully loaded {len(histograms)} histograms")
    
    # Create 2D histogram
    hist_2d = plotter.create_2d_histogram(histograms, valid_labels, args.hist_name)
    
    if not hist_2d:
        print("Error: Failed to create 2D histogram")
        sys.exit(1)
    
    # Generate output filename if not provided
    if args.output_name:
        output_name = args.output_name
    else:
        if len(decay_types) > 1:
            decay_str = "both"
        else:
            decay_str = decay_types[0]
        ctau_str = "_".join(ctau_list)
        output_name = (f"2D_{args.hist_name}_gluino{args.gluino_mass}_"
                      f"chi10{args.neutralino_mass}_{decay_str}_{ctau_str}")
    
    # Save the plot
    plotter.save_2d_plot(hist_2d, output_name, args.log_scale_z)
    
    print("2D histogram creation completed successfully!")

if __name__ == "__main__":
    main()
