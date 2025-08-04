import { useState, useEffect } from 'react';
import { Tabs } from '@mantine/core';
import '../src/custom_css/my_css.css'
import Home from './home'
import { Inbox } from './inbox';
import { Invoces } from './incovces';
import { SOPs } from './standard_ops';
import { Orders } from './orders';
import { Payments } from './payments';
import { Helmet } from 'react-helmet';
import { send_message_to_agent, insert_new_item_api } from '../APIs/api';
import { insert_new_purchas_api } from '../APIs/purchase_api';
import { insert_new_ticket_api, get_all_tickets_api} from '../APIs/ticket_api'
import { get_all_orders_api } from '../APIs/orders_api';
import { get_all_sop_cats_api } from '../APIs/sop_cats_api'
import { get_all_payments_api } from '../APIs/payments_api';
import { Item, Purchase, Ticket } from '../custom_types/models';



export function Menu() {
  
  const [activeTab, setActiveTab] = useState('home');
  const [agentResponse, setAgentResponse] = useState();
  const [tickets, setTickets] = useState([]);
  const [sop_cats, setSop_cats] = useState([]);
  const [orders, setOrders] = useState([]);
  const [payments, setPayments] = useState([]);

  async function run_test_api(){
    const results = await send_message_to_agent('hi')
    return results['response']
  }

  async function get_all_tickets (){
    // console.log('msdfff')
    const res = await get_all_tickets_api()
    return res
  }

  async function get_all_sop_cats (){
    const res = await get_all_sop_cats_api()
    return res
  }

  async function get_all_orders (){
    const res = await get_all_orders_api()
    return res
  }

  async function get_all_payments (){
    const res = await get_all_payments_api()
    return res
  }

  function handleCiteClick(){
    
    setActiveTab('inbox')
    run_test_api().then((res)=>{
      setAgentResponse(res)
      console.log(res)
    }).catch((error)=>{
      console.error(error)
    })
    
   
    get_all_tickets().then(
      (res)=>{
        
        setTickets(res)
    })
  

  }

  useEffect(() => {
    const titles = {
      home: 'Home',
      inbox: 'Inbox',
      sops: 'Standard Operating Procedure',
      orders: 'Orders',
      payments: 'Payments',
      invoices: 'Invoces',
    };

    document.title = titles[activeTab];

  }, [activeTab]);

  useEffect(() => {
// console.log('setting all tickets0000.')
    get_all_tickets().then(
      (res)=>{
        setTickets(res)
      })    
      .catch((error) => {
      console.log('Failed to fetch tickets:', error)
    })

      get_all_sop_cats().then(
      (res)=>{
        setSop_cats(res)
      })

      get_all_orders().then(
        (res)=>{
          setOrders(res)
        }
      )

      get_all_payments().then(
        (res)=>{
          // console.log(res)
          setPayments(res)
        }
      )


      

  }, []);


  return (
    <Tabs value={activeTab} onChange={setActiveTab}>
      <Tabs.List grow>
        <Tabs.Tab className='custom-font-tab' value="home">Home</Tabs.Tab>
        <Tabs.Tab className='custom-font-tab' value="inbox">Inbox</Tabs.Tab>
        <Tabs.Tab className='custom-font-tab' value="sops">Standard Operating Procedure</Tabs.Tab>
        <Tabs.Tab className='custom-font-tab' value="orders">Orders</Tabs.Tab>
        <Tabs.Tab className='custom-font-tab' value="payments">Payments</Tabs.Tab>
        <Tabs.Tab className='custom-font-tab' value="invoices">Invoces</Tabs.Tab>
      </Tabs.List>

      <Tabs.Panel value="home"><Home clickHandler={handleCiteClick}/></Tabs.Panel>
      <Tabs.Panel value="inbox"><Inbox agent_response={agentResponse} tickets={tickets} /></Tabs.Panel>
      <Tabs.Panel value="sops"><SOPs sop_cats={sop_cats} /></Tabs.Panel>
      <Tabs.Panel value="orders"><Orders orders={orders} /></Tabs.Panel>
      <Tabs.Panel value="payments"><Payments payments={payments}/></Tabs.Panel>
      <Tabs.Panel value="invoices"><Invoces/></Tabs.Panel>
    </Tabs>
  );
}