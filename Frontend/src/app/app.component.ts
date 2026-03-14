import { Component, ElementRef, ViewChild, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { ChatService, ChatResponse } from './services/chat.service';

interface ChatMessage {
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  routing?: string; // debug info
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  providers: [ChatService],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements AfterViewChecked {
  title = 'PolibAI 2.0';
  messages: ChatMessage[] = [];
  userInput: string = '';
  isTyping: boolean = false;

  @ViewChild('chatScroll') private chatScrollContainer!: ElementRef;

  quickActions = [
    { label: '📚 Riassumi bando Erasmus', prompt: 'Riassumi i requisiti principali del bando Erasmus+ 2026/2027.' },
    { label: '💰 Calcolo Tasse e ISEE', prompt: 'Come funziona la No Tax Area quest\'anno e quali sono le scadenze?' },
    { label: '🤖 Orientamento Robotica', prompt: 'Mi piace la robotica, quali corsi mi offrite e che sbocchi ho?' },
    { label: '🏢 Aziende Partner', prompt: 'Quali sono le aziende partner con cui collaborate per stage in ambito IT?' }
  ];

  constructor(private chatService: ChatService) {
    // Initial greeting
    this.messages.push({
      text: '👋 Ciao! Sono PolibAI 2.0, l\'assistente virtuale del Politecnico di Bari. Come posso aiutarti oggi a scegliere il tuo percorso o a navigare tra le pratiche amministrative?',
      sender: 'bot',
      timestamp: new Date()
    });
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  scrollToBottom(): void {
    try {
      this.chatScrollContainer.nativeElement.scrollTop = this.chatScrollContainer.nativeElement.scrollHeight;
    } catch (err) {}
  }

  sendQuickAction(prompt: string) {
    this.userInput = prompt;
    this.sendMessage();
  }

  sendMessage() {
    if (!this.userInput.trim()) return;

    const userMsg = this.userInput.trim();
    this.messages.push({
      text: userMsg,
      sender: 'user',
      timestamp: new Date()
    });
    
    this.userInput = '';
    this.isTyping = true;

    this.chatService.askPolibAI(userMsg).subscribe({
      next: (response: ChatResponse) => {
        this.messages.push({
          text: response.reply,
          sender: 'bot',
          timestamp: new Date(),
          routing: response.debug_routing
        });
        this.isTyping = false;
      },
      error: (err) => {
        this.messages.push({
          text: '❌ Si è verificato un errore di connessione col server PolibAI. Riprova più tardi.',
          sender: 'bot',
          timestamp: new Date()
        });
        this.isTyping = false;
        console.error(err);
      }
    });
  }
}
