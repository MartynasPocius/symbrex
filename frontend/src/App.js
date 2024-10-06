import './App.css';
import './index.css';
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Intro from './Intro';
import Main from './Main';

function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path='/' element = {<Intro/>}/>
          <Route path='/main' element = {<Main/>}/>
        </Routes>
      </div>
    </Router>
  );
}

export default App;
