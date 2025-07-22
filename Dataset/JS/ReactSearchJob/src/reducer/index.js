import { combineReducers } from 'redux-immutable';
import header from './header';
import table from './table';
import { ymap, mapState } from './ymap';
import vacancyCard from './vacancyCard';

export const Reducers = combineReducers({
  header,
  table,
  vacancyCard,
});
