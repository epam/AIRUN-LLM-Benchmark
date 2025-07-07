import { createStore, applyMiddleware } from 'redux';
import ReduxThunk from 'redux-thunk';
import {fromJS} from 'immutable';
import {Reducers as rootReducer} from '../reducer';

const middlewares = [ReduxThunk];
const enhancer = [applyMiddleware(...middlewares)];

export default function configureStore(initialState = {}) {
  return createStore(rootReducer, fromJS(initialState), ...enhancer);
}
