import { LOAD_VACANCY, START, SUCCESS, FAIL } from '../constants';

// Response from https://api.work/vacancies/${vacancyId} => interface DetailedVacancyItem

// interface DetailedVacancyItem extends VacancyItem {
//   key_skills: Array<{ name: string }>;
//   description: string;
// }

export function loadVacancy(vacancyId) {
  return dispatch => {
    dispatch({
      type: LOAD_VACANCY + START,
      payload: { isLoad: false },
    });

    const baseUrl = `https://api.work/vacancies/${vacancyId}`;
    fetch(`${baseUrl}`)
      .then(resp => {
        if (resp.ok) {
          return resp.json();
        }
        throw new Error('Something went wrong ...');
      })
      .then(vacancy =>
        dispatch({
          type: LOAD_VACANCY + SUCCESS,
          payload: { vacancy, isLoad: true },
        }),
      )
      .catch(error =>
        dispatch({
          type: LOAD_VACANCY + FAIL,
          payload: { isLoad: true, error },
        }),
      );
  };
}
