import { SimpleChange } from "@angular/core"

export type SimpleChanges<T> = {
  [key in keyof T]: SimpleChange;
}