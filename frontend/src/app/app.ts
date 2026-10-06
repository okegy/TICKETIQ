import { Component, OnInit, ChangeDetectorRef, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CubeWaveComponent } from './cube-wave';
import { TRANSLATIONS, LangCode } from './i18n';

declare const window: any;

export interface ResolutionStep {
  stepNumber: number;
  instruction: string;
  sourceArticleId: string;
  sourceSection: string;
  sourceStepId: string;
  verificationStatus: string;
}

export interface EvidenceItem {
  articleId: string;
  title: string;
  score: number;
  sharedEvidence: string[];
  sourceExcerpt: string;
}

export interface DuplicateMatch {
  ticketId: string;
  title: string;
  similarityScore: number;
  status: string;
}

export interface KnowledgeGap {
  proposedTopic: string;
  patternKeyword: string;
  affectedTicketCount: number;
  recommendation: string;
}

export interface KnowledgeArticle {
  articleId: string;
  title: string;
  category: string;
  subcategory: string;
  symptoms: string[];
  possibleCause: string;
  prerequisites: string[];
  steps: { sourceStepId: string; order: number; text: string }[];
  validation: string;
  escalationCondition: string;
  keywords: string[];
  version: string;
}

export interface DatasetSimilarTicket {
  ref: string;
  subject: string;
  queue: string;
  type: string;
  priority: string;
  score: number;
}

export interface AnalysisResult {
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
    retrievalRelevance: number;
    ticketCompleteness: number;
    sourceAgreement: number;
    groundingCoverage: number;
    rationale: string[];
  };
  language: {
    code: string;
    name: string;
    native: string;
    requested: string;
  };
  localized: {
    decisionMessage: string;
    escalationSuggestion: string;
    sanitizedNote: string;
    kbNote: string;
    datasetSignalLabel: string;
    detectedLanguageLabel: string;
  };
  datasetSignal: {
    queue: string | null;
    confidence: number;
    basedOn: number;
    similarTickets: DatasetSimilarTicket[];
  };
}

export interface BotAvatar {
  id: string;
  name: string;
  emoji: string;
  role: string;
  description: string;
}

export interface ChatMsg {
  sender: 'user' | 'bot';
  avatar?: string;
  text: string;
  time: string;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, CubeWaveComponent],
  templateUrl: './app.html',
  styleUrls: ['./app.css']
})
export class App implements OnInit {
  activeTab = 'workspace';

  // The app runs zoneless (Angular 21 default): async callbacks must mark
  // the view dirty explicitly or the UI never re-renders.
  private cdr = inject(ChangeDetectorRef);

  // Ticket Inputs
  ticketInput = 'User cannot log in, account locked after too many failed login attempts. Contact: admin@corp.com or 555-0199.';
  applicationName = 'Identity Admin Console';
  confidenceThreshold = 0.15;
  
  loading = false;
  analysisResult: AnalysisResult | null = null;
  errorMessage = '';
  actionMessage = '';
  ticketStatus = 'DRAFT';

  feedbackHelpful: boolean | null = null;
  feedbackNotes = '';
  feedbackSubmitted = false;

  activeDrawerArticle: KnowledgeArticle | null = null;

  // Clerk Auth State
  clerkUser: any = null;
  clerkLoaded = false;

  // Priority decision (fetched after analysis)
  priorityDecision: { priority: string; urgency: string; rationale: string; matchedRules: string[] } | null = null;

  // Batch CSV Triage State
  batchFile: File | null = null;
  batchResults: any[] = [];
  batchLoading = false;
  batchThreshold = 0.15;
  batchError = '';

  // Toggle Chatbot State
  chatbotOpen = false;
  selectedAvatar = 'Atlas';
  chatInput = '';
  chatSending = false;

  avatars: BotAvatar[] = [
    { id: 'Atlas', name: 'Atlas', emoji: '🏛️', role: 'IT Architect', description: 'Deep technical runbook citations' },
    { id: 'Nova', name: 'Nova', emoji: '✨', role: 'AI Guide', description: 'Evidence meters & PII protection' },
    { id: 'Spark', name: 'Spark', emoji: '⚡', role: 'Triage Specialist', description: 'Fast troubleshooting shortcuts' }
  ];

  chatMessages: ChatMsg[] = [
    {
      sender: 'bot',
      avatar: 'Atlas',
      text: "Hello! I am Atlas, your TicketIQ agentic assistant. How can I assist with your ticket diagnosis or knowledge base resolution?",
      time: 'Just now'
    }
  ];

  knowledgeCatalog: KnowledgeArticle[] = [];

  async loadKnowledgeCatalog() {
    try {
      const res = await fetch('http://127.0.0.1:8000/ai/knowledge-articles');
      if (res.ok) {
        const data = await res.json();
        this.knowledgeCatalog = (data.articles || []).map((a: any) => ({
          articleId: a.articleId,
          title: a.title,
          category: a.category,
          subcategory: a.subcategory,
          symptoms: a.symptoms || [],
          possibleCause: a.possibleCause || '',
          prerequisites: a.prerequisites || [],
          steps: a.steps || [],
          validation: a.validation || '',
          escalationCondition: a.escalationCondition || '',
          keywords: a.keywords || [],
          version: a.version || '1.0'
        }));
        this.cdr.markForCheck();
      }
    } catch (_) {
      // KB catalog stays empty; source drawer is guarded by *ngIf.
    }
  }

  duplicates: DuplicateMatch[] = [];

  knowledgeGaps: KnowledgeGap[] = [
    {
      proposedTopic: 'Troubleshooting Kubernetes Ingress Controller Timeouts',
      patternKeyword: 'ingress',
      affectedTicketCount: 4,
      recommendation: 'Multiple recurring microservice gateway errors mention ingress timeouts. Recommend authoring an approved cluster ingress runbook.'
    },
    {
      proposedTopic: 'Multi-Factor Authenticator (MFA) Device Re-Enrollment',
      patternKeyword: 'authenticator',
      affectedTicketCount: 3,
      recommendation: 'Frequent lockouts after phone hardware replacements. Create a self-service QR code reset guide.'
    }
  ];

  dashboardStats = {
    totalAnalyzed: 142,
    groundedDraftsRate: 91,
    needsReviewCount: 14,
    noMatchCount: 12,
    avgResponseTimeSec: 1.8,
    accuracyRate: 100.0
  };

  evaluationData = {
    datasetName: 'Verification Kit — 12 KB articles / 20 labeled tickets (2026-10-06)',
    categoryAccuracy: 100.0,
    top1HitRate: 100.0,
    top3HitRate: 100.0,
    refusalPrecision: 100.0,
    groundingCoverage: 100.0,
    falseRefusalRate: 0.0
  };

  simulatedThreshold = 0.15;

  // ── Multilingual (en / hi / ta) ────────────────────────────────
  // Signal: reading it inside t()/tf() makes every template binding that
  // calls them re-render instantly on language change (zoneless-safe).
  uiLanguage = signal<LangCode>('en');
  supportedLanguages: { code: LangCode; name: string; native: string }[] = [];

  t(key: string): string {
    const table = TRANSLATIONS[this.uiLanguage()] ?? TRANSLATIONS['en'];
    return table[key] ?? TRANSLATIONS['en'][key] ?? key;
  }

  tf(key: string, ...vals: (string | number)[]): string {
    let out = this.t(key);
    vals.forEach((v, i) => { out = out.replace(`{${i}}`, String(v)); });
    return out;
  }

  chatPlaceholder(): string {
    return this.tf('chat.ph', this.selectedAvatar);
  }

  async loadLanguages() {
    try {
      const res = await fetch('http://127.0.0.1:8000/ai/languages');
      if (res.ok) {
        const data = await res.json();
        this.supportedLanguages = data.languages || [];
        this.cdr.markForCheck();
      }
    } catch (_) { /* selector falls back to translations */ }
  }

  ngOnInit() {
    this.initClerk();
    this.loadKnowledgeCatalog();
    this.loadLanguages();
    this.loadEvaluationSweep();
  }

  initClerk() {
    const checkClerkInterval = setInterval(() => {
      if (typeof window !== 'undefined' && window.Clerk) {
        clearInterval(checkClerkInterval);
        try {
          window.Clerk.load().then(() => {
            this.clerkLoaded = true;
            if (window.Clerk.user) {
              this.clerkUser = window.Clerk.user;
            }
            this.cdr.markForCheck();
          });
        } catch (e) {
          console.warn('Clerk load notice:', e);
        }
      }
    }, 500);
  }

  openClerkSignIn() {
    if (typeof window !== 'undefined' && window.Clerk) {
      window.Clerk.openSignIn();
    } else {
      alert('Clerk Authentication is still loading — try again in a moment.');
    }
  }

  openClerkUserProfile() {
    if (typeof window !== 'undefined' && window.Clerk && window.Clerk.user) {
      window.Clerk.openUserProfile();
    }
  }

  clerkSignOut() {
    if (typeof window !== 'undefined' && window.Clerk) {
      window.Clerk.signOut().then(() => {
        this.clerkUser = null;
      });
    }
  }

  setTab(tab: string) {
    this.activeTab = tab;
    this.actionMessage = '';
  }

  toggleChatbot() {
    this.chatbotOpen = !this.chatbotOpen;
  }

  selectAvatar(avatarId: string) {
    this.selectedAvatar = avatarId;
    const av = this.avatars.find(a => a.id === avatarId);
    this.chatMessages.push({
      sender: 'bot',
      avatar: avatarId,
      text: `Switched to ${av?.name} (${av?.role}). ${av?.description}. How can I help?`,
      time: 'Now'
    });
  }

  async sendChatMessage(prefilledText?: string) {
    const textToSend = prefilledText || this.chatInput;
    if (!textToSend.trim() || this.chatSending) return;

    this.chatMessages.push({
      sender: 'user',
      text: textToSend,
      time: 'Now'
    });
    this.chatInput = '';
    this.chatSending = true;
    this.cdr.markForCheck();

    try {
      const res = await fetch('http://127.0.0.1:8000/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          avatar: this.selectedAvatar,
          message: textToSend,
          language: this.uiLanguage()
        })
      });

      if (res.ok) {
        const data = await res.json();
        this.chatMessages.push({
          sender: 'bot',
          avatar: this.selectedAvatar,
          text: data.reply,
          time: 'Now'
        });
      } else {
        this.chatMessages.push({
          sender: 'bot',
          avatar: this.selectedAvatar,
          text: this.t('chat.err'),
          time: 'Now'
        });
      }
    } catch (err: any) {
      this.chatMessages.push({
        sender: 'bot',
        avatar: this.selectedAvatar,
        text: this.tf('chat.connectErr', String(err.message || err)),
        time: 'Now'
      });
    } finally {
      this.chatSending = false;
      this.cdr.markForCheck();
    }
  }

  async analyzeTicket() {
    if (!this.ticketInput.trim()) return;
    
    this.loading = true;
    this.errorMessage = '';
    this.actionMessage = '';
    this.analysisResult = null;
    this.feedbackSubmitted = false;
    this.duplicates = [];

    try {
      const response = await fetch('http://127.0.0.1:8000/ai/analyze-ticket', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticketId: 'INC-' + Math.floor(1000 + Math.random() * 9000),
          ticketText: this.ticketInput,
          structuredFields: { application: this.applicationName },
          confidenceThreshold: this.confidenceThreshold,
          // Ticket language is auto-detected from content; the selector
          // only controls the interface language and the chat language.
          language: 'auto'
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      this.analysisResult = await response.json();
      this.ticketStatus = this.analysisResult?.decision === 'DRAFT_ALLOWED' ? 'ANALYZED' : 'NO_RELIABLE_MATCH';
      this.cdr.markForCheck();

      this.checkDuplicates();
      // Fetch priority immediately after analysis
      if (this.analysisResult) {
        await this.fetchPriorityDecision();
      }

    } catch (err: any) {
      this.errorMessage = this.tf('err.connect', String(err.message || err));
    } finally {
      this.loading = false;
      this.cdr.markForCheck();
    }
  }

  async checkDuplicates() {
    try {
      const res = await fetch('http://127.0.0.1:8000/ai/find-duplicates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticketText: this.ticketInput,
          historicalTickets: [
            { id: 'INC-1082', title: 'Account locked after failed logins', rawDescription: 'User cannot log in, account locked after too many failed login attempts', status: 'RESOLVED' },
            { id: 'INC-1045', title: 'Password reset email not received', rawDescription: 'User did not receive the password reset email after requesting a reset', status: 'RESOLVED' },
            { id: 'INC-1019', title: 'Nightly batch job failed', rawDescription: 'Nightly batch job failed with step error, needs re-run', status: 'RESOLVED' }
          ],
          threshold: 0.35
        })
      });
      if (res.ok) {
        const data = await res.json();
        this.duplicates = data.duplicates || [];
        this.cdr.markForCheck();
      }
    } catch (_) {}
  }

  openSourceDrawer(articleId: string) {
    const found = this.knowledgeCatalog.find(a => a.articleId === articleId);
    if (found) {
      this.activeDrawerArticle = found;
    }
  }

  closeSourceDrawer() {
    this.activeDrawerArticle = null;
  }

  approveResolution() {
    this.ticketStatus = 'APPROVED';
    this.actionMessage = this.t('msg.approved');
  }

  rejectResolution() {
    this.ticketStatus = 'REJECTED';
    this.actionMessage = this.t('msg.rejected');
  }

  submitFeedback(helpful: boolean) {
    this.feedbackHelpful = helpful;
    this.feedbackSubmitted = true;
    this.actionMessage = helpful ? this.t('msg.fb.pos') : this.t('msg.fb.neg');
  }

  loadSampleTicket(type: string) {
    if (type === 'lockout') {
      this.ticketInput = 'User cannot log in, account locked after too many failed login attempts. Contact: admin@corp.com';
      this.applicationName = 'Identity Admin Console';
    } else if (type === 'reset') {
      this.ticketInput = 'Password reset email not received, user requested a reset twice and nothing arrived in inbox or spam.';
      this.applicationName = 'Identity Portal';
    } else if (type === 'batch') {
      this.ticketInput = 'Nightly batch job failed during the reconciliation step. Needs investigation and re-run.';
      this.applicationName = 'Batch Scheduler';
    } else if (type === 'nomatch') {
      this.ticketInput = 'The coffee machine on 4th floor breakroom is out of espresso beans.';
      this.applicationName = 'Facility Support';
    }
    this.actionMessage = '';
    this.feedbackSubmitted = false;
  }

  // ── Real threshold evaluation (GET /ai/evaluate-thresholds) ────
  evaluationSweep: {
    dataset: { tickets: number; matchExpected: number; noMatchExpected: number };
    tunedThreshold: number;
    safeWindow: { min: number; max: number } | null;
    minMatchedScore: number | null;
    maxUnmatchedScore: number | null;
    sweep: { threshold: number; coverage: number; refusalAccuracy: number; falseRefusals: number; groundedDrafts: number }[];
  } | null = null;

  async loadEvaluationSweep() {
    try {
      const res = await fetch('http://127.0.0.1:8000/ai/evaluate-thresholds');
      if (res.ok) {
        this.evaluationSweep = await res.json();
        this.cdr.markForCheck();
      }
    } catch (_) { /* chart stays hidden if service is down */ }
  }

  activeSweepPoint() {
    if (!this.evaluationSweep) return null;
    const t = Math.round(this.simulatedThreshold * 20) / 20;
    return this.evaluationSweep.sweep.find(s => Math.abs(s.threshold - t) < 0.001) || null;
  }

  chartX(t: number): number {
    return 20 + ((t - 0.05) / 0.85) * 560;
  }

  chartY(pct: number): number {
    return 200 - (pct / 100) * 180;
  }

  coveragePoints(): string {
    if (!this.evaluationSweep) return '';
    return this.evaluationSweep.sweep
      .map(s => `${this.chartX(s.threshold).toFixed(1)},${this.chartY(s.coverage).toFixed(1)}`)
      .join(' ');
  }

  safetyPoints(): string {
    if (!this.evaluationSweep) return '';
    return this.evaluationSweep.sweep
      .map(s => `${this.chartX(s.threshold).toFixed(1)},${this.chartY(s.refusalAccuracy).toFixed(1)}`)
      .join(' ');
  }

  tunedX(): number {
    return this.chartX(this.evaluationSweep?.tunedThreshold ?? 0.15);
  }

  safeWindowX(): number {
    const w = this.evaluationSweep?.safeWindow;
    return w ? this.chartX(w.min) : 0;
  }

  safeWindowW(): number {
    const w = this.evaluationSweep?.safeWindow;
    return w ? this.chartX(w.max) - this.chartX(w.min) : 0;
  }

  // ── Priority Decision ──────────────────────────────────────────────────────

  async fetchPriorityDecision() {
    if (!this.analysisResult) return;
    try {
      const res = await fetch('http://127.0.0.1:8000/ai/priority', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticketText: this.analysisResult.redactedText || this.ticketInput,
          category: this.analysisResult.classification?.category || '',
          subcategory: this.analysisResult.classification?.subcategory || ''
        })
      });
      if (res.ok) {
        this.priorityDecision = await res.json();
        this.cdr.markForCheck();
      }
    } catch (_) {
      // Priority is a bonus feature — failure is silent
    }
  }

  // ── Batch CSV Triage ──────────────────────────────────────────────────────

  onBatchFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.batchFile = input.files[0];
      this.batchError = '';
      this.batchResults = [];
    }
  }

  async runBatchTriage() {
    if (!this.batchFile) return;
    this.batchLoading = true;
    this.batchError = '';
    this.batchResults = [];

    const formData = new FormData();
    formData.append('file', this.batchFile);
    formData.append('confidenceThreshold', String(this.batchThreshold));

    try {
      const res = await fetch('http://127.0.0.1:8000/ai/batch-triage', {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }

      const data = await res.json();
      this.batchResults = data.results || [];
      this.cdr.markForCheck();
    } catch (err: any) {
      this.batchError = this.tf('batch.err', String(err.message || err));
    } finally {
      this.batchLoading = false;
      this.cdr.markForCheck();
    }
  }

  exportBatchResults() {
    const blob = new Blob([JSON.stringify(this.batchResults, null, 2)], {
      type: 'application/json'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ticketiq_batch_results_${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }
}

