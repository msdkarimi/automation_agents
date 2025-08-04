import { Table, Button, Modal, Select, Divider, Group, SimpleGrid, Badge, ActionIcon, Pill, Stack, Card, Code, Accordion, Text, Container , Box, Space, Loader} from '@mantine/core';
import { IconCirclesRelation, IconRobot, IconBrain, IconDots, IconTool, IconPlayerPlay, IconMessageChatbot } from '@tabler/icons-react';
import { useElementSize } from '@mantine/hooks';
import { useState} from 'react';
import { AgentActions } from '../../custom_types/models';
import { start_chat_with_case_context_agent } from '../../APIs/agent_api';


export function MyTable(props) {
  
  const icon = <IconCirclesRelation />;

  const [agent_respondes, setAgent_respondes] = useState([]);


  

  return (
    
    <>
      <Table ta="center" stickyHeader>
        <Table.Thead bg="dark.9">
          <Table.Tr>
            <Table.Th ta="center">Subject</Table.Th>
            <Table.Th ta="center">Received</Table.Th>
            <Table.Th ta="center">Status</Table.Th>
            <Table.Th ta="center">Actions</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {props.elements.map((element) => (
            <Row
              key={element.id}
              element={element}
              open={props.open}
              close={props.close}
              selection={props.selection}
              setSelection={props.setSelection}
              opened={props.opened}
              agent_response={props.agent_response}
              agent_respondes={agent_respondes}
              setAgent_respondes={setAgent_respondes}
              modal2Opened={props.modal2Opened}
              setModal2Opened={props.setModal2Opened}
              eventSourceRef={props.eventSourceRef}

            />
          ))}
        </Table.Tbody>
      </Table>
    </>
  );
}

function Row(props) {
  return (
    <>
      <Table.Tr>
        <Table.Td>{props.element.subject}</Table.Td>
        <Table.Td>{props.element.date_received}</Table.Td>
        <Table.Td>{props.element.status=='close'? <Badge   variant="gradient" gradient={{ from: 'green', to: 'lime', deg: 196 }}>Close</Badge> : <Badge  variant="gradient" gradient={{ from: 'pink', to: 'red', deg: 90  }}>Open</Badge>  }</Table.Td>
        <Table.Td>
        <ActionIcon
            variant="light"
            color="gray"
            aria-label="Settings"
            onClick={() => {
              props.setSelection(props.element); // Set the selected element
              props.open(); // Open the modal
            }}
          >
          <IconDots style={{ width: '70%', height: '70%' }} stroke={1.5} />
        </ActionIcon>
        </Table.Td>
      </Table.Tr>

      <Modal
        opened={props.opened && props.selection?.id === props.element.id} // Only open for the selected row
        onClose={() => {
          props.close();
          props.setSelection(null); // Clear selection on close
        }}
        title={props.element.subject}
        size="80%"
      >
        {props.selection && (
          <ModalContent agent_response={props.agent_response} selection={props.selection} setSelection={props.setSelection} 
          agent_respondes={props.agent_respondes} setAgent_respondes={props.setAgent_respondes} modal2Opened={props.modal2Opened}
              setModal2Opened={props.setModal2Opened} eventSourceRef={props.eventSourceRef} />
        )}
      </Modal>
    </>
  );
}

function ModalContent(props){
  const { ref, width, height } = useElementSize();

  const[caseContextThink, setCaseContextThink] = useState([]);
  const[caseContextChat, setCaseContextChat] = useState([]);
  const[caseContextTool, setCaseContextTool] = useState([]);

  const[interaction, setInterction] = useState([]);

   async function init_chat (){
      const res = await start_chat_with_case_context_agent(props.selection.id, props.selection.customer_id, props.selection.customer_comment)
      return res
    }

  const caseContextHandler = ()=>{
      props.setModal2Opened((oldvalue)=>{return !oldvalue})

      


      init_chat().then(
        (sse)=>{
          props.eventSourceRef.current = sse
          sse.onmessage = (event) => {
            if (event.data === '[DONE]') {
              sse.close();
            } 
            else {
              const chat_bot = JSON.parse(event.data)

              if (chat_bot.type === 'agent'){
                if (chat_bot.phase === 'start'){
                  props.setAgent_respondes((old_vlaues)=>{
                    return [...old_vlaues, new AgentActions(chat_bot.id, true, null)]
                  })
                }
                else {
                  props.setAgent_respondes((old_vlaues)=>{
                    return [...old_vlaues, new AgentActions(chat_bot.id, null, true)]
                  })
                }
              }

              else if (chat_bot.type === 'loop'){
                // agent_respondes, setAgent_respondes

                props.setAgent_respondes((old_vlaues)=>{
                  return [...old_vlaues, new AgentActions(chat_bot.id, null, null)]
                })
              }
              // else if (chat_bot.type === 'tool'){
              //   props.setAgent_respondes((old_vlaues)=>{
              //     return [...old_vlaues, new AgentActions(chat_bot.id, null, null, [], [], [chat_bot])]
              //   })
              // }

              if (chat_bot.type === "chat" && chat_bot.think ){
                props.setAgent_respondes(prevItems => {
                      
                        const newItems = [...prevItems];
                        const lastItem = newItems[newItems.length - 1]
                        const updateItem = new AgentActions(
                          lastItem.the_id,
                          null,
                          null,
                          [...lastItem.think, chat_bot.content],
                          lastItem.chat, 
                          lastItem.tool
                        )

                        newItems[newItems.length - 1] = updateItem;
                        return newItems;
            
                      });
                  }
              else if (chat_bot.type === "chat" && !chat_bot.think){
                props.setAgent_respondes(prevItems => {
                      
                        const newItems = [...prevItems];
                        const lastItem = newItems[newItems.length - 1]
                        const updateItem = new AgentActions(
                          lastItem.the_id,
                          null,
                          null,
                          lastItem.think,
                          [...lastItem.chat, chat_bot.content], 
                          lastItem.tool
                        )
                        newItems[newItems.length - 1] = updateItem;
                        return newItems;
                        
                      });
              }
              else if (chat_bot.type === "tool"){
                props.setAgent_respondes(prevItems => {
                      
                        const newItems = [...prevItems];
                        const lastItem = newItems[newItems.length - 1]
                        const updateItem = new AgentActions(
                          lastItem.the_id,
                          null,
                          null,
                          lastItem.think,
                          lastItem.chat, 
                          [...lastItem.tool, chat_bot]
                        )
                        newItems[newItems.length - 1] = updateItem;
                        return newItems;
                        
                      });
              }

          

              
            }
            sse.onerror = (err) => {
              console.error('EventSource failed:', err);
            sse.close();
      };};

          

        
        })

  }
  

  let has_links = props.selection.ticket_links

  let order_id = null 
  let payment_id = null
  let purchase_id = null
  let sop_id = null

  if (has_links)
  {
    if(has_links.order_id)
      order_id = has_links.order_id

    if(has_links.payment_id)
      payment_id = has_links.payment_id

    if(has_links.purchase_id)
      purchase_id = has_links.purchase_id

    if(has_links.sop_id)
      sop_id = has_links.sop_id
  }


  return(
    <SimpleGrid cols={1} spacing="xs">
              <div>
                <p><strong>Customer ID:</strong> <Pill color="cyan">{props.selection.customer_id}</Pill></p>
                <p><strong>Date:</strong> <Pill color="cyan">{props.selection.date_received}</Pill> </p>

                {order_id ? <p><strong>Order ID:</strong> <Pill color="cyan">{order_id}</Pill></p> :<></>}
                {payment_id ? <p><strong>Payment ID:</strong> <Pill color="cyan">{payment_id}</Pill></p> :<></>}
                {purchase_id ? <p><strong>Purchase ID:</strong> <Pill color="cyan">{purchase_id}</Pill></p> :<></>}
                {sop_id ? <p><strong>Sop. ID:</strong> <Pill color="cyan">{sop_id}</Pill></p> :<></>}
              </div>
              <div >
              <Group align="center" spacing="sm">
                <strong>Status:</strong> 
                
                <Select placeholder="Pick value" data={['close','open']} value={props.selection.status}
                
                onChange={(new_value)=>{
                  if (new_value != null){
                  props.setSelection((old_state)=>
                    ({...old_state, status:new_value})
                  )
                }

                }}
                />
                
              </Group>
              </div>
              <div>
                <textarea readOnly value={props.selection.customer_comment || ''} className='my_text_area' ref={ref} />
              </div>
              
              <div>

              <textarea ref={ref} className='my_text_area' />
                {/* <Textarea
                  description="Your Response:"
                  placeholder="Type Your Response Here"
                  // value={props.agent_response}
                /> */}
              </div>

              <Group gap="xs">
                <Button leftSection={<IconRobot size={18} />} variant="light" color="orange">Draft Reply Agent</Button> <Button variant="outline" color="lime">Reply</Button>
              </Group>
            
            <div>
              <Divider my="md" variant="dashed"/>
            </div>
  
            <Group justify="flex-end" gap="xs">
          <Button onClick={caseContextHandler} leftSection={<IconRobot size={18} />} variant="filled" color="violet">Invoke Case Contex Agent</Button> <Button leftSection={<IconRobot size={18} />} variant="filled" color="pink">Invoke Standard Operating Procedure Agent</Button>
        </Group>
        
        <CaseContextAgent setCaseContextThink={setCaseContextThink} caseContextThink={caseContextThink} eventSourceRef={props.eventSourceRef} agent_respondes={props.agent_respondes} setAgent_respondes={props.setAgent_respondes}  setModal2Opened={props.setModal2Opened} modal2Opened={props.modal2Opened} />

        </SimpleGrid>

  );
}


function CaseContextAgent(props){

  const on_modal_close_handler = ()=>{
    props.setModal2Opened(false);
    props.eventSourceRef.current.close();
    props.setAgent_respondes([])
  }
  return(

      <Modal
        size='xl'
        opened={props.modal2Opened}
        onClose={on_modal_close_handler}
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <IconMessageChatbot/> <span>Case contex Agent:</span>
           </div>
        }
      >


      <Stack
      h='100%'
      align="stretch"
      justify="center"
      gap="xs"
      radius={0}
    >
      {props.agent_respondes.map((elem) => 
        ( 
          // console.log(elem);
          <Rows2 key={elem.the_id} agent_respondes={elem} />
        )
)}
    </Stack>    
      </Modal>
  );
}


function Rows2(props){

  const icon_tool = <IconTool/>;

  // console.log(props.agent_respondes.think)
  if (!props.agent_respondes.is_start && !props.agent_respondes.is_end){
    // console.log(props.agent_respondes)
  return (
    <Container w="100%" h="100%">
      <Box >
        <Card bg="#e8ebe9fb" shadow="xl" padding="lg" radius="md" mt={10} mb={10}  w="100%" h="100%">
          <Accordion>
            <Accordion.Item  key={props.agent_respondes.the_id} value={props.agent_respondes.the_id}>
              <Accordion.Control  bg="rgba(184, 184, 184, 0.3)" icon={<IconBrain/>} >Thoughts</Accordion.Control>
              <Accordion.Panel>{props.agent_respondes.think.length > 0 ? props.agent_respondes.think.map((_)=>_) : <Loader color="blue"  /> }</Accordion.Panel>
            </Accordion.Item>
          </Accordion>
          <Space h="xs" />
          <Group>
            <AgentAction agent_respondes={props.agent_respondes}  />
          </Group>
        </Card>
      </Box>
  </Container>  
)}
else if (props.agent_respondes.is_start)
  return(
    <Container  w="100%" h="100%">
      <Card bg="#27a32dff" shadow="sm" padding="lg" radius="md" mt={10} mb={10}  w="100%" h="100%">
        <Group>
          <IconPlayerPlay/>
          <Box>
            <Text >
              Mounting agent ...
            </Text>
          </Box>
        </Group>
      </Card>
    </Container>
)
else if (props.agent_respondes.is_end)
  return(
    <Container  w="100%" h="100%">
      <Card bg="#27a32dff" shadow="sm" padding="lg" radius="md" mt={10} mb={10}  w="100%" h="100%">
        <Box>
          <Text>
            Unmounting agent....
          </Text>
        </Box>
      </Card>
    </Container>
)
}


function AgentAction (props){
  if (props.agent_respondes.tool.length > 0) {
    return(
      <>
        <Space h="xs" />
        <Box >
          <Group>
            <Text>
               Tool calling:
            </Text>
              <Code>
                {props.agent_respondes.tool[0].name} ( { JSON.stringify(props.agent_respondes.tool[0].args)} )
              </Code>
          </Group>
        </Box>    
      </>
    )
  }
  else if(props.agent_respondes.chat.length > 0){
    return (
      <>
        <Space h="xs" />
        <Box >
          <Text>
            {props.agent_respondes.chat.map((_)=>_)}
          </Text>
        </Box>
      </>
    )
  }
  return(
    <>
      <Space h="xs" />
      <Loader color="gray" type="dots" /> thinking
    </>
  )
}