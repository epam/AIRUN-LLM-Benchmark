import React from 'react';
import './loader.css';

export const loader = (
  <div className="indicator">
    <svg width="16px" height="12px">
      <polyline id="back" points="1 6 4 6 6 11 10 1 12 6 15 6" />
      <polyline id="front" points="1 6 4 6 6 11 10 1 12 6 15 6" />
    </svg>
  </div>
);

export const parseQuery = (queryString) => {
  const query = {};
  let pairs = (queryString[0] === '?' ? queryString.substr(1) : queryString).split('&');
  for (let i = 0; i < pairs.length; i++) {
    let pair = pairs[i].split('=');
    query[decodeURIComponent(pair[0])] = decodeURIComponent(pair[1] || '');
  }
  return query;
};