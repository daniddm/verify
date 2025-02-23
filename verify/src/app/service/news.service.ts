// news.service.ts
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

interface AnalysisResponse {
  probability: number;
}

@Injectable({
  providedIn: 'root'
})
export class NewsService {
  private apiUrl = 'http://localhost:8080/api/analyze';

  constructor(private http: HttpClient) {}

  analyzeNews(text: string): Observable<AnalysisResponse> {
    return this.http.post<AnalysisResponse>(this.apiUrl, { text });
  }
}