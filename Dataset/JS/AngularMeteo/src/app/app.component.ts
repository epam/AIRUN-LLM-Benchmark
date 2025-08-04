import { ChangeDetectionStrategy, Component, ViewEncapsulation } from '@angular/core';
import { HistoricalComponent } from '../historical/historical.component';
import { HeaderComponent } from '../header/header.component';

@Component({
  selector: 'mto-app',
  imports: [HeaderComponent, HistoricalComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
  encapsulation: ViewEncapsulation.None,
})
export class AppComponent {
  protected loading = false;
  protected error: Error | undefined;
}
