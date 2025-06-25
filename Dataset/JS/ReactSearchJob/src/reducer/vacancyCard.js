import { fromJS } from 'immutable';
import { LOAD_VACANCY, START, SUCCESS, FAIL } from '../constants';

const initialState = fromJS({
  vacancies: [],
  isLoad: false,
});

export default (state = initialState, { type, payload }) => {
  switch (type) {
    case LOAD_VACANCY + START:
      return state.setIn(['isLoad'], payload.isLoad);

    case LOAD_VACANCY + SUCCESS:
      return state
        .setIn(['isLoad'], payload.isLoad)
        .setIn(['error'], null)
        .updateIn(['vacancies'], vacanciesArr =>
          vacanciesArr.push(fromJS(payload.vacancy)),
        );

    case LOAD_VACANCY + FAIL:
      return state
        .setIn(['isLoad'], payload.isLoad)
        .setIn(['error'], payload.error);

    default:
      return state;
  }
};
