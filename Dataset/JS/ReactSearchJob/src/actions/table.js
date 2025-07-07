import {
  LOAD_TABLE_DATA,
  LOAD_PAGE_TABLE_DATA,
  CHANGE_VACANCIES_PAGE,
  START,
  SUCCESS,
  FAIL,
} from '../constants';

// Response from https://api.work/vacancies${params}&area=1 => interface VacancyResponse;

// interface VacancyResponse = {
//   items: Array<{
//     id: string;
//     name: string;
//     salary?: {
//       from?: number;
//       to?: number;
//       currency?: string;
//     };
//     salary_range: any;
//     address?: {
//       city?: string;
//       lat?: number;
//       lng?: number;
//       metro?: {
//         station_name: string;
//       };
//     };
//     employer?: {
//       id: string;
//       name: string;
//       logo_urls?: {
//         original?: string;
//         "90"?: string;
//         "240"?: string;
//       };
//     };
//     snippet?: {
//       requirement: string;
//       responsibility: string;
//     };
//   }>;
//   found: number;
//   pages: number;
//   page: number;
//   per_page: number;
// };

export function loadData(params, push) {
  return dispatch => {
    dispatch({
      type: LOAD_TABLE_DATA + START,
      payload: { data: [], isLoad: false, isLoadData: true },
    });
    const baseUrl = `https://api.work/vacancies${params || '?'}&area=1`;
    fetch(`${baseUrl}`)
      .then(resp => {
        push && push();
        if (resp.ok) {
          return resp.json();
        }
        throw new Error('Something went wrong ...');
      })
      .then(data =>
        dispatch({
          type: LOAD_TABLE_DATA + SUCCESS,
          payload: {
            data: data.items,
            isLoad: true,
            isLoadData: true,
            found: data.found,
            page: data.page,
            pages: data.pages,
            params,
          },
        }),
      )
      .catch(error =>
        dispatch({
          type: LOAD_TABLE_DATA + FAIL,
          payload: {
            isLoad: true,
            error,
          },
        }),
      );
  };
}

export function changeVacanciesPage(page) {
  return {
    type: CHANGE_VACANCIES_PAGE,
    payload: { page },
  };
}

export function loadPage(params, page) {
  return dispatch => {
    dispatch({
      type: LOAD_PAGE_TABLE_DATA + START,
      payload: { isLoad: false },
    });
    const baseUrl = `https://api.work/vacancies${params ||
      '?'}&area=1&page=${page}`;
    fetch(`${baseUrl}`)
      .then(resp => {
        if (resp.ok) {
          return resp.json();
        }
        throw new Error('Something went wrong ...');
      })
      .then(resp =>
        dispatch({
          type: LOAD_PAGE_TABLE_DATA + SUCCESS,
          payload: {
            data: resp.items,
            isLoad: true,
            page,
          },
        }),
      )
      .catch(error => {
        dispatch({
          type: LOAD_PAGE_TABLE_DATA + FAIL,
          payload: {
            isLoad: true,
            error,
          },
        });
      });
  };
}
