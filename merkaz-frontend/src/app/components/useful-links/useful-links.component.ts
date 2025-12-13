import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-useful-links',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './useful-links.component.html',
  styleUrls: ['./useful-links.component.css', '../dashborad/admin-dash/admin-dash-shared.css']
})
export class UsefulLinksComponent {
  openLink(url: string) {
    window.open(url, '_blank');
  }
}

