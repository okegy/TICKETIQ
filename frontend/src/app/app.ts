import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface ResolutionStep {
  stepNumber: number;
  instruction: string;
  sourceArticleId: string;
  sourceSection: string;
  sourceStepId: string;
  verificationStatus: string;
}

interface EvidenceItem {
  articleId: string;
  title: string;
  score: number;
  sharedEvidence: string[];
  sourceExcerpt: string;
}

interface AnalysisResult {
  decision: string;
  redactedText: string;
  classification: {
    category: string;
    subcategory: string;
    confidence: number;
  };
  evidence: EvidenceItem[];
  resolutionSteps: ResolutionStep[];
  escalation: {
    required: boolean;
    condition?: string;
    sourceArticleId?: string;
  };
  confidence: {
    finalScore: number;
    rationale: string[];
  };
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrls: ['./app.css']
})
export class App {
  title = 'TicketIQ — Evidence-Gated IT Support Copilot';
  
  ticketInput = 'Payroll staff cannot log in after password reset. AUTH-401 error displayed on screen. About 18 users affected. Contact: admin@corp.com or 555-0199.';
  applicationName = 'Payroll Portal';
  confidenceThreshold = 0.50;
  
  loading = false;
  analysisResult: AnalysisResult | null = null;
  errorMessage = '';

  async analyzeTicket() {
    if (!this.ticketInput.trim()) return;
    
    this.loading = true;
    this.errorMessage = '';
    this.analysisResult = null;

    try {
      const response = await fetch('http://localhost:8000/ai/analyze-ticket', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticketId: 'INC-' + Math.floor(1000 + Math.random() * 9000),
          ticketText: this.ticketInput,
          structuredFields: { application: this.applicationName },
          confidenceThreshold: this.confidenceThreshold
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      this.analysisResult = await response.json();
    } catch (err: any) {
      this.errorMessage = 'Failed to connect to AI Service: ' + (err.message || err);
    } finally {
      this.loading = false;
    }
  }

  loadSampleTicket(type: string) {
    if (type === 'payroll') {
      this.ticketInput = 'Payroll staff cannot log in after password reset. AUTH-401 error displayed on screen. Contact: supervisor@company.com';
      this.applicationName = 'Payroll Portal';
    } else if (type === 'vpn') {
      this.ticketInput = 'GlobalProtect VPN fails to connect with ERR_GATEWAY_UNREACHABLE on remote laptop.';
      this.applicationName = 'GlobalProtect';
    } else if (type === 'unmatched') {
      this.ticketInput = 'The coffee machine on 4th floor breakroom is out of espresso beans.';
      this.applicationName = 'Facility Support';
    }
  }
}
