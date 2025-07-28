import { Blockquote, Center, Box, ScrollArea, Loader} from '@mantine/core';
import { IconMailbox } from '@tabler/icons-react';
import { MyTable } from './tabels/inbox_table';
import { useDisclosure } from '@mantine/hooks';
import { useState, useEffect } from 'react';

export function Inbox(props) {

  const icon = <IconMailbox />;

  const [selectedRow, setSelectedRow] = useState(null);
  const [opened, { open, close }] = useDisclosure(false);


  // useEffect(()=>{
  //   if (selectedRow != null)
  //     console.log(selectedRow)
  // }
  // , [selectedRow])

  return (
  // 1. The outer wrapper sets the maximum height.
    // This creates the boundary for our component.
    <Box className='limited-height-flex custom-font-body'>

      {/* 2. The inner container fills the wrapper and manages the layout.
          It now has a defined height to distribute to its children. */}
      <Blockquote color="lime" icon={icon} mt="xl" className='fill-flex-column' >
        {/* 3. The scrollable area grows to fill the remaining space.
            Since its parent (Blockquote) has a defined height, scrolling now works. */}
        <ScrollArea className='my_grow my_border_radius'>
        <Center  bg="var(--mantine-color-gray-light)" >
        {
          props.tickets.length!=0 ?
          <MyTable agent_response={props.agent_response} elements={props.tickets} selection={selectedRow} setSelection={setSelectedRow} opened={opened} open={open} close={close}/>
          :
          <Loader size={50} /> 
        }
        </Center>

        </ScrollArea>
        </Blockquote>
    </Box>
  );
}






