import { ChangeDetectionStrategy, Component, input, output, ViewEncapsulation } from '@angular/core';
import { SimpleChanges } from '../../types';

@Component({
  selector: 'mto-button',
  templateUrl: './button.component.html',
  styleUrl: './button.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
  encapsulation: ViewEncapsulation.None,
})
export class ButtonComponent<T> {
  public label = input<string>();

  public submit = output();
}
