// app.component.ts
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NewsService } from './service/news.service';
import { HttpClientModule } from '@angular/common/http';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FormsModule, HttpClientModule, CommonModule],
  providers: [NewsService],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent {
  title = 'fake-news';
  newsText: string = '';
  result: number | null = null;

  constructor(private newsService: NewsService) {}

  public analyzeNews() {
    if (this.newsText) {
      this.newsService.analyzeNews(this.newsText).subscribe({
        next: (response) => {
          this.result = response.probability;
        },
        error: (error) => {
          console.error('Error:', error);
        },
      });
    }
  }
}