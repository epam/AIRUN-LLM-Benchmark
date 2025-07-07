import React from 'react';
import PropTypes from 'prop-types';

const TextBox = ({ onChange, onKeyDown, value = '' }) => (
  <input
    className="form-control"
    placeholder="Vacancy name or key word"
    type="text"
    value={value}
    onKeyDown={e => onKeyDown(e)}
    onChange={e => onChange(e.target.value)}
  />
);
TextBox.propTypes = {
  onChange: PropTypes.func.isRequired,
  onKeyDown: PropTypes.func.isRequired,
  value: PropTypes.string.isRequired,
};
export default TextBox;
