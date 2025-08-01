export interface AutocompleteDatasource<T> {
  search(term: string): Promise<AutocompleteItem<T>[]>;
}

export interface AutocompleteItem<T> {
  label: string;
  value: T;
}