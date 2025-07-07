import React from 'react';
import { Link } from 'react-router-dom';
import PropTypes from 'prop-types';

export const JobItem = ({ item }) => (
  <div className="card mb-3">
    <div className="card-body">
      {item.getIn(['employer', 'logo_urls']) && (
        <img
          src={item.getIn(['employer', 'logo_urls', '90'])}
          className="float-right vacancy-sm-icon"
          alt={item.getIn(['employer', 'name'])}
        />
      )}
      <h5 className="card-title">
        <Link to={`/vacancy/${item.get('id')}`} className="card-link">
          {item.get('name')}
        </Link>
      </h5>
      <h6 className="card-subtitle mb-2 text-muted mb-3 mt-2">
        {item.getIn(['employer', 'name'])}
        {item.get('address') && item.getIn(['address', 'metro'])
          ? `, ${item.getIn(['address', 'metro', 'station_name'])}`
          : ''}
      </h6>
      <h6 className="card-subtitle mb-2 text-muted">
        {`Salary ${
          item.get('salary')
            ? (item.getIn(['salary', 'from'])
                ? `from ${item.getIn(['salary', 'from'])} `
                : '') +
              (item.getIn(['salary', 'to'])
                ? `to ${item.getIn(['salary', 'to'])} `
                : '') +
              item.getIn(['salary', 'currency'])
            : 'not defined'
        }`}
      </h6>
      <p
        className="card-text"
        /* eslint-disable */
        dangerouslySetInnerHTML={{
          __html:
            item.getIn(['snippet', 'requirement']) && window.innerWidth < 768
              ? `${item.getIn(['snippet', 'requirement']).substring(0, 70)}...`
              : item.getIn(['snippet', 'requirement']),
        }}
        /* eslint-enable */
      />
      <p
        className="card-text"
        /* eslint-disable */
        dangerouslySetInnerHTML={{
          __html:
            item.getIn(['snippet', 'responsibility']) && window.innerWidth < 768
              ? `${item
                .getIn(['snippet', 'responsibility'])
                .substring(0, 70)}...`
              : item.getIn(['snippet', 'responsibility']),
        }}
      /* eslint-enable */
      />
    </div>
  </div>
);
JobItem.propTypes = {
  item: PropTypes.objectOf(PropTypes.any).isRequired,
};
export default JobItem;
