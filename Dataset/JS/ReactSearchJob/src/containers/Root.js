import React from 'react';
import { HashRouter as Router, Route } from 'react-router-dom';
import pure from 'recompose/pure';
import { Provider } from 'react-redux';
import configureStore from '../store';
import { Home } from './Home';

const Root = () => (
  <Provider store={configureStore()}>
    <Router>
      <Route path="/" component={Home} />
    </Router>
  </Provider>
);

export default pure(Root);
