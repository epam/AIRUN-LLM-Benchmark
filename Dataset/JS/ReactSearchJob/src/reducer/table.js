import { fromJS } from 'immutable';
import {
  LOAD_TABLE_DATA,
  LOAD_PAGE_TABLE_DATA,
  CHANGE_VACANCIES_PAGE,
  START,
  SUCCESS,
  FAIL,
} from '../constants';

const initialState = fromJS({
  data: [],
  isLoadData: false,
  isLoad: true,
  found: '',
  page: 0,
  pages: 0,
  params: '',
});

export default (state = initialState, { type, payload }) => {
  switch (type) {
    case LOAD_TABLE_DATA + START:
      return state
        .setIn(['data'], fromJS(payload.data))
        .setIn(['isLoad'], payload.isLoad)
        .setIn(['isLoadData'], payload.isLoadData);

    case LOAD_TABLE_DATA + SUCCESS:
      return fromJS({
        errors: null,
        data: [
          {
            items: payload.data,
            page: payload.page,
          },
        ],
        isLoad: payload.isLoad,
        isLoadData: payload.isLoadData,
        found: payload.found,
        page: payload.page,
        pages: payload.pages,
        params: payload.params,
      });

    case LOAD_TABLE_DATA + FAIL:
      return state
        .setIn(['isLoad'], payload.isLoad)
        .setIn(['error'], payload.error);

    // Reducer for adding page

    case LOAD_PAGE_TABLE_DATA + START:
      return state.setIn(['isLoad'], false);

    case LOAD_PAGE_TABLE_DATA + SUCCESS:
      return state
        .setIn(['page'], payload.page)
        .setIn(['isLoad'], payload.isLoad)
        .update('data', data =>
          data.push(
            fromJS({
              items: payload.data,
              page: payload.page,
            }),
          ),
        );

    case LOAD_PAGE_TABLE_DATA + FAIL:
      return state
        .setIn(['isLoad'], payload.isLoad)
        .setIn(['error'], payload.error);

    case CHANGE_VACANCIES_PAGE:
      return state.setIn(['page'], payload.page);

    default:
      return state;
  }
};
