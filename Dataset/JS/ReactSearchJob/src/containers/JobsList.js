import React, { PureComponent } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import ReactPaginate from 'react-paginate';
import { loader } from '../helpers';
import { JobItem } from '../components/JobItem';
import { loadData, loadPage, changeVacanciesPage } from '../actions';
import noJobs from '../nojobs.jpg';

class JobsList extends PureComponent {
  static propTypes = {
    table: PropTypes.objectOf(PropTypes.any).isRequired,
    location: PropTypes.objectOf(PropTypes.any).isRequired,
    loadData: PropTypes.func.isRequired,
    changeVacanciesPage: PropTypes.func.isRequired,
    loadPage: PropTypes.func.isRequired,
  };

  componentDidMount() {
    const params = decodeURIComponent(this.props.location.search);
    const tableParams = this.props.table.get('params');
    const isLoadData = this.props.table.get('isLoadData');
    const isLoad = this.props.table.get('isLoad');

    if (params !== tableParams && isLoad && !isLoadData) {
      this.props.loadData(params);
    }
  }

  handlePageClick = ({ selected }) => {
    const { table } = this.props;
    const params = this.props.location.search;
    const data = table.get('data');
    const isDownload = data.find(item => item.get('page') === selected);
    window.scrollTo(0, 0);
    if (isDownload) {
      this.props.changeVacanciesPage(selected);
    } else {
      this.props.loadPage(params, selected);
    }
  };

  renderLoader = () => (
    <div className="position-relative" style={{ minHeight: '150px' }}>
      {loader}
    </div>
  );

  renderList = () => {
    const { table } = this.props;
    const data = table.get('data');
    const page = table.get('page');
    const pages = table.get('pages');
    const found = table.get('found');

    const currPage =
      data.size > 0 ? data.find(item => item.get('page') === page) : 0;

    return (
      <div className="mt-3">
        <h3 className="text-center">Found {found} vacancies</h3>
        {currPage
          .get('items')
          .map(item => <JobItem item={item} key={item.get('id')} />)}
        <div className="justify-content-center">
          <ReactPaginate
            previousLabel={'«'}
            nextLabel={'»'}
            disableInitialCallback
            breakLabel={<button className="page-link">...</button>}
            breakClassName={'page-item'}
            pageCount={pages}
            initialPage={page}
            marginPagesDisplayed={1}
            pageRangeDisplayed={4}
            onPageChange={this.handlePageClick}
            containerClassName={'pagination justify-content-center'}
            pageClassName={'page-item'}
            previousClassName={'page-item'}
            nextClassName={'page-item'}
            pageLinkClassName={'page-link'}
            previousLinkClassName={'page-link'}
            nextLinkClassName={'page-link'}
            activeClassName={'active'}
          />
        </div>
      </div>
    );
  };

  render() {
    const { table } = this.props;
    const isLoad = table.get('isLoad');
    const isLoadData = table.get('isLoadData');
    const error = table.get('error');

    if (error) {
      return (
        <div className="text-center mt-4">
          <h4>Ops, error...</h4>
          <button
            className="btn btn-outline-dark my-3"
            onClick={() => this.props.history.push('/')}
          >
            To main
          </button>
        </div>
      );
    }
    if (!isLoad) {
      return this.renderLoader();
    }

    if (!isLoadData) {
      return <h3 className="text-center my-5">Make search!</h3>;
    }

    const found = table.get('found');
    if (!found) {
      return (
        <div className="mt-3">
          <h3 className="text-center">Ops...nothing was found</h3>
          <div className="text-center">
            <img src={noJobs} alt="no jobs" />
          </div>
        </div>
      );
    }

    return this.renderList();
  }
}
export default connect(
  state => ({
    table: state.get('table'),
  }),
  { loadData, loadPage, changeVacanciesPage },
)(JobsList);
