import { fromJS } from 'immutable';
import {
  LOAD_METRO,
  CHANGE_SELECTION,
  CHANGE_SEARCHTEXT,
  START,
  SUCCESS,
  FAIL,
} from '../constants';

const initialState = fromJS({
  searchText: '',
  metroId: '',
  metro: [],
  isLoad: false,
});

export default (state = initialState, action) => {
  const { type, payload } = action;

  switch (type) {
    case LOAD_METRO + START:
      return state.setIn(['isLoad'], payload.isLoad);

    case LOAD_METRO + SUCCESS:
      return state
        .setIn(['metro'], fromJS(payload.metro))
        .setIn(['isLoad'], payload.isLoad);

    case LOAD_METRO + FAIL:
      return state.setIn(['isLoad'], false);

    case CHANGE_SELECTION:
      return state.setIn(['metroId'], payload.selected);

    case CHANGE_SEARCHTEXT:
      return state.setIn(['searchText'], payload.text);

    default:
      return state;
  }
};
