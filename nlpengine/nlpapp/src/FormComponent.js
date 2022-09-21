import React, { Component } from 'react';
import axios from 'axios';
import ModalComponent from './ModalComponent';
import OverlayComponent from './OverlayComponent';
import { Button, Form, FormGroup, Label, Input } from 'reactstrap';
import './style.css';

const NLP_ENGINE_URL = 'http://localhost:5000/';

function findUniqueNumTopics(array) {
        var flags = [], output = [], l = array.length, i;
        for( i=0; i<l; i++) {
                if( flags[array[i].Topic]) continue;
                flags[array[i].Topic] = true;
                output.push(array[i].Topic);
        }
        return output;
}

class FormComponent extends Component {
        hasUnmounted = false;

        constructor() {
                super();

                this.state = {
                        companies: '',
                        quarters: '',
                        currentModel:'',
                        isOpen: false,
                        isLoading: false,
                        models: [],
                        wordCloud:[],
                        modelToEdit: '',
                        model_name: '',
                        isApply: false,
                        other: false,
                };
                this.handleSubmit = this.handleSubmit.bind(this);
                this.changeHandler = this.changeHandler.bind(this);
                this.handleEditModel = this.handleEditModel.bind(this);
                this.updateEditModel = this.updateEditModel.bind(this);
                this.handleApplyModel = this.handleApplyModel.bind(this);
                this.handleViewModel = this.handleViewModel.bind(this);

                axios.post(NLP_ENGINE_URL + 'getmodels')
                .then(res => {
                        this.setState(prevState => ({
                                models: res.data.split('thisisaseperator')
                        }));
                });

        }
        componentWillReceiveProps(props) {
                this.setState({
                        companies: props.companies,
                        quarters: props.quarters
                });
        }


        changeHandler = event => {
                const target = event.target;
                const value = target.type === 'companies' ? target.checked : target.value;
                const name = target.name;

                this.setState({
                        [name]: value,
                        isOpen: false,
                        other: false,
                        isApply: false,

                });
        }

        handleSubmit(event) {
                event.preventDefault();
                if(this.state.model_name === '' || this.state.quarters === '' || this.state.companies === '') {
                        return 'invalid input';
                }
                this.setState(prevState => ({
                        isLoading: !prevState.isLoading
                }));

                axios.post(NLP_ENGINE_URL + 'buildmodel', this.state)
                .then(res => {
                        console.log(res.data);
                        var result = [];
                        for(var x in res.data) {
                                result.push({"Topic": res.data[x].Topic, "Word": res.data[x].Word, "Frequency": res.data[x].Frequency})
                        }
                        var numTopics = findUniqueNumTopics(result);
                        var wordCloud = [];

                        for (var j = 0; j < numTopics.length; j++) {
                                wordCloud[j] = [];
                        }
                        var counter = 0;
                        for (var i = 0; i < res.data.length;i++) {
                                if(counter === res.data[i].Topic) {
                                        wordCloud[counter].push({"text": res.data[i].Word, "value": Math.abs(res.data[i].Frequency) * 150})
                                }
                                else {
                                        counter++;
                                        wordCloud[counter].push({"text": res.data[i].Word, "value": Math.abs(res.data[i].Frequency) * 150})
                                }
                        }

                        this.setState(prevState => ({
                                currentModel: result,
                                wordCloud: wordCloud,
                                isOpen: true,
                                isLoading: false,
                                other:true,
                                isApply: false
                        }));
                        axios.post(NLP_ENGINE_URL + 'getmodels')
                        .then(res => {
                                this.setState(prevState => ({
                                        models: res.data.split('thisisaseperator')
                                }));
                        });
                }).catch(error => {
                        console.log(error.response)
                        this.setState(prevState => ({
                                isLoading: !prevState.isLoading    }));
                        });
                }

                updateEditModel(e) {
                        var temp = e.target.value;
                        this.setState(prevState => ({
                                modelToEdit: temp
                        }));
                }

                handleViewModel(event) {
                        event.preventDefault();
                        this.setState(prevState => ({
                                isLoading: !prevState.isLoading
                        }));

                        axios.post(NLP_ENGINE_URL + 'viewmodel', this.state).then(res => {
                                console.log(res.data);

                                var result = [];
                                for(var x in res.data) {
                                        result.push({"Topic": res.data[x].Topic, "Word": res.data[x].Word, "Frequency": res.data[x].Frequency})
                                }
                                var numTopics = findUniqueNumTopics(result);
                                var wordCloud = [];

                                for (var j = 0; j < numTopics.length; j++) {
                                        wordCloud[j] = [];
                                }
                                var counter = 0;
                                for (var i = 0; i < res.data.length;i++) {
                                        if(counter === res.data[i].Topic) {
                                                wordCloud[counter].push({"text": res.data[i].Word, "value": Math.abs(res.data[i].Frequency) * 150})
                                        }
                                        else {
                                                counter++;
                                                wordCloud[counter].push({"text": res.data[i].Word, "value": Math.abs(res.data[i].Frequency) * 150})
                                        }
                                }

                                console.log(wordCloud);
                                this.setState(prevState => ({
                                        currentModel: result,
                                        wordCloud: wordCloud,
                                        isOpen: true,
                                        isLoading: false,
                                        other:true,
                                        isApply: false
                                }));
                        }).catch(error => {
                                console.log(error.response);
                                this.setState(prevState => ({
                                        isLoading: !prevState.isLoading }));
                                });

                }

                handleEditModel(event) {
                        event.preventDefault();
                        if(this.state.quarters === '' || this.state.companies === '') {
                                return 'invalid input';
                        }
                        this.setState(prevState => ({
                                isLoading: !prevState.isLoading
                        }));
                        axios.post(NLP_ENGINE_URL + 'editmodel', this.state).then(res => {
                                console.log(res.data);
                                var result = [];
                                for(var x in res.data) {
                                        result.push({"Topic": res.data[x].Topic, "Word": res.data[x].Word, "Frequency": res.data[x].Frequency})
                                }
                                var numTopics = findUniqueNumTopics(result);
                                var wordCloud = [];

                                for (var j = 0; j < numTopics.length; j++) {
                                        wordCloud[j] = [];
                                }
                                var counter = 0;
                                for (var i = 0; i < res.data.length;i++) {
                                        if(counter === res.data[i].Topic) {
                                                wordCloud[counter].push({"text": res.data[i].Word, "value": Math.abs(res.data[i].Frequency) * 150})
                                        }
                                        else {
                                                counter++;
                                                wordCloud[counter].push({"text": res.data[i].Word, "value": Math.abs(res.data[i].Frequency) * 150})
                                        }
                                }

                                this.setState(prevState => ({
                                        currentModel: result,
                                        wordCloud: wordCloud,
                                        isOpen: true,
                                        isLoading: false,
                                        other:true,
                                        isApply: false,
                                }));
                        }).catch(error => {
                                console.log(error.response)
                                this.setState(prevState => ({
                                        isLoading: !prevState.isLoading    }));
                                });
                        }

                        handleApplyModel(event) {
                                event.preventDefault();
                                if(this.state.quarters === '' || this.state.companies === '') {
                                        return 'invalid input';
                                }
                                this.setState(prevState => ({
                                        isLoading: !prevState.isLoading,
                                        other: false
                                }));

                                axios.post(NLP_ENGINE_URL + 'applymodel', this.state).then(res => {
                                        console.log(res.data);
                                        this.setState(prevState => ({
                                                other:false,
                                                isApply: true,
                                                currentModel: res.data,
                                                isOpen: true,
                                                isLoading: false,
                                        }));

                                        //https://www.commonlounge.com/discussion/99e86c9c15bb4d23a30b111b23e7b7b1
                                        // Term frequency: doc.count(w)/total words in doc
                                        //Inverse Document Frequency: idf(w) = log(total number of documents/number of documents containing word w)
                                        //Term Frequency-Inverse Document Frequency: Tf-idf(w) = tf(w)*idf(w)
                                        //The more important a word is in the document, it would get a higher tf-idf score and vice versa.
                                        //topic distribution for the given document bow, as a list of (topic_id, topic_probability) 2-tuples.

                                }).catch(error => {
                                        console.log(error.response)
                                        this.setState(prevState => ({
                                                isLoading: !prevState.isLoading    }));


                                        });
                                }

                                render () {
                                        return ( <div>
                                                {this.props.build && <div>
                                                        <OverlayComponent isLoading={this.state.isLoading}> </OverlayComponent>
                                                        <h3> Build a New Model</h3>
                                                        <Form onSubmit={this.handleSubmit}>

                                                                <FormGroup>
                                                                        <Label> Model Name:

                                                                                <Input placeholder='modelName' name="model_name" type="model_name"
                                                                                        value={this.state.model_name}
                                                                                        onChange={this.changeHandler}
                                                                                        /></Label>
                                                                        </FormGroup>

                                                                        <FormGroup>
                                                                                <Label> List of Company Tickers:

                                                                                        <Input name="companies" type="companies"
                                                                                                placeholder='PEP MSFT MMM'                 checked={this.state.companies}
                                                                                                onChange={this.changeHandler}
                                                                                                /></Label>
                                                                                </FormGroup>

                                                                                <FormGroup >
                                                                                        <Label> Range of Quarters:
                                                                                                <Input name="quarters" type="quarters"
                                                                                                        placeholder='1Q12->4Q17'
                                                                                                        value={this.state.quarters}
                                                                                                        onChange={this.changeHandler}
                                                                                                        /></Label>

                                                                                        </FormGroup>
                                                                                        <Button type="submit">Build My Model</Button>
                                                                                </Form>
                                                                                <ModalComponent other={this.state.other} apply={this.state.isApply} action={this.changeHandler}  modal={this.state.isOpen} currentModel={this.state.currentModel}
                                                                                        wordCloud={this.state.wordCloud} companies={this.state.companies} quarters={this.state.quarters}> </ModalComponent> </div> }

                                                                                        {this.props.edit && <div>                            <OverlayComponent isLoading={this.state.isLoading}> </OverlayComponent> <h3>Edit A Saved Model</h3>
                                                                                <Form onSubmit={this.handleEditModel}>
                                                                                        <FormGroup>
                                                                                                <Label for="exampleSelect">Select a Model
                                                                                                        <Input type="select" name="select" id="exampleSelect" onChange={this.updateEditModel}>
                                                                                                                {this.state.models.map((model) => <option key={model}> {model} </option>)}
                                                                                                        </Input></Label>
                                                                                                </FormGroup>

                                                                                                <FormGroup>
                                                                                                        <Label> List of Company Tickers:

                                                                                                                <Input name="companies" type="companies"
                                                                                                                        placeholder='PEP MSFT MMM'                 checked={this.state.companies}
                                                                                                                        onChange={this.changeHandler}
                                                                                                                        /></Label>
                                                                                                        </FormGroup>

                                                                                                        <FormGroup >
                                                                                                                <Label> Range of Quarters:
                                                                                                                        <Input name="quarters" type="quarters"
                                                                                                                                placeholder='1Q12->4Q17'
                                                                                                                                value={this.state.quarters}
                                                                                                                                onChange={this.changeHandler}
                                                                                                                                /></Label>

                                                                                                                </FormGroup>
                                                                                                                <Button type="submit">Apply new corpus to my model</Button>
                                                                                                        </Form>
                                                                                                        <ModalComponent other={this.state.other}
                                                                                                                apply={this.state.isApply}
                                                                                                                action={this.changeHandler}  modal={this.state.isOpen} currentModel={this.state.currentModel}
                                                                                                                wordCloud={this.state.wordCloud} companies={this.state.companies} quarters={this.state.quarters}> </ModalComponent>
                                                                                                </div>}
                                                                                                {this.props.apply && <div><OverlayComponent isLoading={this.state.isLoading}> </OverlayComponent>

                                                                                        <h3>Apply a Saved Model to New Documents</h3>
                                                                                        <Form onSubmit={this.handleApplyModel}>
                                                                                                <FormGroup>
                                                                                                        <Label for="exampleSelect">Select a Model
                                                                                                                <Input type="select" name="select" id="exampleSelect" onChange={this.updateEditModel}>
                                                                                                                        {this.state.models.map((model) => <option key={model}> {model} </option>)}
                                                                                                                </Input></Label>
                                                                                                        </FormGroup>

                                                                                                        <FormGroup>
                                                                                                                <Label> List of Company Tickers:

                                                                                                                        <Input name="companies" type="companies"
                                                                                                                                placeholder='PEP MSFT MMM'                 checked={this.state.companies}
                                                                                                                                onChange={this.changeHandler}
                                                                                                                                /></Label>
                                                                                                                </FormGroup>

                                                                                                                <FormGroup >
                                                                                                                        <Label> Range of Quarters:
                                                                                                                                <Input name="quarters" type="quarters"
                                                                                                                                        placeholder='1Q12->4Q17'
                                                                                                                                        value={this.state.quarters}
                                                                                                                                        onChange={this.changeHandler}
                                                                                                                                        /></Label>

                                                                                                                        </FormGroup>
                                                                                                                        <Button type="submit">Apply Selected Model to New Documents</Button>
                                                                                                                </Form>
                                                                                                                <ModalComponent other={this.state.other} apply={this.state.isApply} action={this.changeHandler}  modal={this.state.isOpen} currentModel={this.state.currentModel}></ModalComponent>

                                                                                                        </div>}
                                                                                                        {this.props.view && <div><OverlayComponent isLoading={this.state.isLoading}> </OverlayComponent>

                                                                                                <h3>View a Saved Model</h3>
                                                                                                <Form onSubmit={this.handleViewModel}>
                                                                                                        <FormGroup>
                                                                                                                <Label for="exampleSelect">Select a Model
                                                                                                                        <Input type="select" name="select" id="exampleSelect" onChange={this.updateEditModel}>
                                                                                                                                {this.state.models.map((model) => <option key={model}> {model} </option>)}
                                                                                                                        </Input></Label>
                                                                                                                </FormGroup>


                                                                                                                                <Button type="submit">View Model Topics</Button>
                                                                                                                        </Form>
                                                                                                                        <ModalComponent other={this.state.other} apply={this.state.isApply} action={this.changeHandler}  wordCloud={this.state.wordCloud} modal={this.state.isOpen} currentModel={this.state.currentModel}></ModalComponent>

                                                                                                                </div>}



                                                                                                </div>
                                                                                        );
                                                                                }
                                                                        }
                                                                        //https://reactstrap.github.io/components/form/
                                                                        export default FormComponent;