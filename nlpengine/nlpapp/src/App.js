import React, { Component } from 'react';
import './App.css';
import FormComponent from './FormComponent';
import { Dropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';

class App extends Component {
        constructor(props) {
                super(props);
                this.state = {buildModel: {companies: '', quarters:''},      dropdownOpen: false,
                buildComponent: false,
                editComponent: false,
                applyComponent:false,
                viewComponent: false

        };
        this.toggle = this.toggle.bind(this);
        this.buildModel = this.buildModel.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.editModel = this.editModel.bind(this);
        this.applyModel = this.applyModel.bind(this);
        this.viewModel = this.viewModel.bind(this);
}

handleSubmit(event) {
        event.preventDefault();
}
toggle() {
        this.setState(prevState => ({
                dropdownOpen: !prevState.dropdownOpen,

        }));
}

buildModel() {
        this.setState(prevState => ({
                buildComponent: !prevState.buildComponent,
                editComponent: false,
                applyComponent: false,
                viewComponent: false

        }));
}

editModel() {
        this.setState(prevState => ({
                buildComponent: false,
                editComponent: !prevState.editComponent,
                applyComponent: false,
                viewComponent: false

        }));
}

applyModel() {
        this.setState(prevState => ({
                buildComponent: false,
                editComponent: false,
                applyComponent: !prevState.applyComponent,
                viewComponent: false
        }));
}
viewModel() {
        this.setState(prevState => ({
                buildComponent: false,
                editComponent: false,
                applyComponent: false,
                viewComponent: !prevState.viewComponent
        }));

}
render() {
        return (
                <div className="App">
                        <h2>Natural Language Processing Tool on Companies&acute; Financial Documents</h2>
                        <Dropdown isOpen={this.state.dropdownOpen} toggle={this.toggle}>
                                <DropdownToggle caret>
                                        What would you Like to do?
                                </DropdownToggle>
                                <DropdownMenu>
                                        <DropdownItem onClick={this.buildModel}> Build a New Model</DropdownItem>
                                        <DropdownItem onClick={this.editModel}> Edit a Saved Model</DropdownItem>
                                        <DropdownItem onClick={this.applyModel}>Apply a Saved Model</DropdownItem>
                                        <DropdownItem onClick={this.viewModel}>View a Saved Model</DropdownItem>

                                </DropdownMenu>
                        </Dropdown>

                        <FormComponent quarters='' companies='' build={this.state.buildComponent} edit={this.state.editComponent} apply={this.state.applyComponent} view={this.state.viewComponent}></FormComponent>
                </div>
        );
}
}

export default App;
//npm start