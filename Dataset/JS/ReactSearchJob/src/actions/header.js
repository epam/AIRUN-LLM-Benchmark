import {
  LOAD_METRO,
  CHANGE_SELECTION,
  CHANGE_SEARCHTEXT,
  START,
  SUCCESS,
  FAIL,
} from '../constants';

// Response from https://api.work/metro/{id} => type Metro
//
// type LineInfo = {
//   id: string;
//   hex_color: string;
//   name: string;
// };
//
// type Station = {
//   id: string;
//   name: string;
//   lat: number;
//   lng: number;
//   order: number;
//   line: LineInfo;
// };
//
// type Line = {
//   id: string;
//   hex_color: string;
//   name: string;
//   stations: Station[];
// };
//
// type Metro = {
//   id: string;
//   name: string;
//   lines: Line[];
// };


export function loadMetro() {
  return dispatch => {
    dispatch({
      type: LOAD_METRO + START,
      payload: { isLoad: false },
    });

    const metroUrl = 'https://api.work/metro/1';
    fetch(`${metroUrl}`)
      .then(response => {
        if (response.ok) {
          return response.json();
        }
        throw new Error('Something went wrong ...');
      })
      .then(metro =>
        dispatch({
          type: LOAD_METRO + SUCCESS,
          payload: { metro: metro.lines, isLoad: true },
        }),
      )
      .catch(error => {
        dispatch({
          type: LOAD_METRO + FAIL,
          payload: { error },
        });
      });
  };
}

export function changeSelection(selected) {
  return {
    type: CHANGE_SELECTION,
    payload: { selected },
  };
}

export function changeTextSearch(text) {
  return {
    type: CHANGE_SEARCHTEXT,
    payload: { text },
  };
}
