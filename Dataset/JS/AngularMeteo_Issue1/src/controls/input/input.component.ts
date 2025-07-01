import { ChangeDetectionStrategy, Component, input, output, ViewEncapsulation } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { SimpleChanges } from '../../types';

@Component({
  selector: 'mto-input',
  templateUrl: './input.component.html',
  styleUrl: './input.component.scss',
  imports: [FormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  encapsulation: ViewEncapsulation.None,
})
export class InputComponent<T> {
  public placeholder = input<string>();
  public value = input<T | undefined>();
  public valueChange = output<T | undefined>();

  protected inputValue: T | undefined;

  public ngOnChanges(changes: SimpleChanges<this>) {
    if (changes.value) {
      this.inputValue = this.value();
    }
  }

  protected async onInputChange() {
    this.valueChange.emit(this.inputValue);
  }
}
