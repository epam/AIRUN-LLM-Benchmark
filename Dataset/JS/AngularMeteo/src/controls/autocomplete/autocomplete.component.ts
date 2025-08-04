import { ChangeDetectionStrategy, Component, input, output, ViewEncapsulation } from '@angular/core';
import { AutocompleteDatasource, AutocompleteItem } from './model';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'mto-autocomplete',
  templateUrl: './autocomplete.component.html',
  styleUrl: './autocomplete.component.scss',
  imports: [FormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  encapsulation: ViewEncapsulation.None,
})
export class AutocompleteComponent<T> {
  public datasource = input.required<AutocompleteDatasource<T>>();
  public placeholder = input<string>();

  public loading = output<boolean>();
  public error = output<Error>();
  public itemSelected = output<T | undefined>();

  protected searchTerm: string | undefined;
  protected results: AutocompleteItem<T>[] = [];

  // TODO: add debounce decorator
  protected async onInputChange() {
    if (!this.searchTerm) {
      this.results = [];
    } else {
      this.loading.emit(true);
      try {
        this.results = await this.datasource().search(this.searchTerm);
      } catch (error) {
        this.error.emit(error as Error);
      } finally {
        this.loading.emit(false);
      }
    }
  }

  protected onItemSelected(item: AutocompleteItem<T>) {
    this.searchTerm = item.label;
    this.itemSelected.emit(item.value);
    this.results = [];
  }
}
