import { Component } from '@angular/core';
import {RouterOutlet} from '@angular/router';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet,MatIconModule],
  templateUrl: './app.html',
  styleUrls: ['./app.css']
})
export class AppComponent {
  protected title = 'merkaz-frontend';
}