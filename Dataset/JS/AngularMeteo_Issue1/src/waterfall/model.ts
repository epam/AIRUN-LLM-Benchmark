export interface WaterfallData {
  columnCount: number;
  rows: (number | undefined)[][];
  timeLabels: string[]; // must be the same length as rows
  columnLabels: string[]; // must be the same length as columnCount
}