import React from 'react';
import { Switch, Route } from 'react-router-dom';
import VacancyPage from './VacancyPage';
import Header from './Header';
import JobsList from "./JobsList";

export const Home = props => {
  const isRoot = props.location.pathname === '/';
  return (
    <div className="wrapper">
      <div className={`main-page${isRoot ? '' : ' hidden'}`}>
        <div className="search-field">
          <Header history={props} />
        </div>
      </div>
      <div className={`container main-layout${isRoot ? '' : ' layout-show'}`}>
        <Switch>
          <Route exact path="/vacancies" component={JobsList} />
          <Route path="/vacancy/:id" component={VacancyPage} />
        </Switch>
      </div>
    </div>
  );
};
