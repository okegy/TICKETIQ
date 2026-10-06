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

interface DuplicateMatch {
  ticketId: string;
  title: string;
  similarityScore: number;
  status: string;
}

interface KnowledgeGap {
  proposedTopic: string;
  patternKeyword: string;
  affectedTicketCount: number;
  recommendation: string;
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
  actionMessage = '';

  // Workflow state
  ticketStatus = 'DRAFT';
  feedbackHelpful: boolean | null = null;
  feedbackNotes = '';
  categoryOverride = '';
  feedbackSubmitted = false;

  // Intelligence state
  duplicates: DuplicateMatch[] = [];
  knowledgeGaps: KnowledgeGap[] = [];
  showIntelligence = false;

  async analyzeTicket() {
    if (!this.ticketInput.trim()) return;
    
    this.loading = true;
    this.errorMessage = '';
    this.actionMessage = '';
    this.analysisResult = null;
    this.feedbackSubmitted = false;
    this.duplicates = [];

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
      this.ticketStatus = this.analysisResult?.decision === 'DRAFT_ALLOWED' ? 'ANALYZED' : 'NO_RELIABLE_MATCH';

      // Check for duplicates
      this.checkDuplicates();

      // Refresh knowledge gap intelligence
      this.fetchKnowledgeGaps();

    } catch (err: any) {
      this.errorMessage = 'Failed to connect to AI Service: ' + (err.message || err);
    } finally {
      this.loading = false;
    }
  }

  async checkDuplicates() {
    try {
      const res = await fetch('http://localhost:8000/ai/find-duplicates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticketText: this.ticketInput,
          historicalTickets: [
            { id: 'INC-1082', title: 'Payroll AUTH-401 login issue', rawDescription: 'Cannot log in after password reset. AUTH-401 error', status: 'RESOLVED' },
            { id: 'INC-1045', title: 'VPN GlobalProtect gateway timeout', rawDescription: 'GlobalProtect VPN failed with ERR_GATEWAY_UNREACHABLE', status: 'RESOLVED' }
          ],
          threshold: 0.35
        })
      });
      if (res.ok) {
        const data = await res.json();
        this.duplicates = data.duplicates || [];
      }
    } catch (_) {}
  }

  async fetchKnowledgeGaps() {
    try {
      const res = await fetch('http://localhost:8000/ai/detect-knowledge-gaps', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          noMatchTickets: [
            { ticketId: 'INC-901', ticketText: 'Kubernetes ingress controller timeout' },
            { ticketId: 'INC-902', ticketText: 'Production kubernetes cluster ingress controller pod crash' },
            { ticketId: 'INC-903', ticketText: 'Cafeteria display screen black' }
          ],
          minClusterSize: 2
        })
      });
      if (res.ok) {
        const data = await res.json();
        this.knowledgeGaps = data.proposedTopics || [];
      }
    } catch (_) {}
  }

  approveResolution() {
    this.ticketStatus = 'APPROVED';
    this.actionMessage = '✅ Resolution approved and saved to ticket audit log.';
  }

  rejectResolution() {
    this.ticketStatus = 'REJECTED';
    this.actionMessage = '🚫 Resolution rejected. Ticket escalated to Tier-2 Engineering.';
  }

  submitFeedback(helpful: boolean) {
    this.feedbackHelpful = helpful;
    this.feedbackSubmitted = true;
    this.actionMessage = helpful 
      ? '👍 Feedback recorded: Analyst validated resolution accuracy.'
      : '👎 Feedback recorded: Analyst flagged insufficient evidence.';
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
    this.actionMessage = '';
    this.feedbackSubmitted = false;
  }
}
